#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import re
from flask import Flask, render_template, request, redirect, url_for, session
import logging
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
from db import db
from models import User, Book, Message
import psycopg2
from search_helper import SearchLogic

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_

import bleach

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

csrf = CSRFProtect(app)
db_correct = db.init_app(app)
ph = PasswordHasher()


def hash_password(password):
    return ph.hash(password)


def verify_password(stored_hash, password):
    try:
        ph.verify(stored_hash, password)
        return True
    except VerifyMismatchError:
        return False


def validate_password(password):
    return bool(
        re.search(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%^&+=.,]).{8,}$", password
        )
    )


def validate_username(username):
    bleach.clean(username)
    return bool(re.search(r"^[a-zA-Z0-9]{3,}$", username))

def validate_text(text):
    return bleach.clean(text)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/part1.html", methods=["GET"])
def login():
    if "username" in session:
        return redirect(url_for("part1_logged_in"))

    return render_template("part1.html")


@app.route("/part1_logged_in", methods=["GET", "POST"])
def part1_logged_in():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("part1_logged_in.html", username=session["username"])


@app.route("/part1_logout", methods = ["POST"])
def part1_logout():
    session.pop("username", None)
    session.pop("password", None)
    return redirect(url_for("login"))


@app.route("/part1_register", methods=["POST"])
def part1_register():

    if "username" in session and "user_type" in session:
        return redirect(url_for("part1_logged_in"))
    try:
        if request.method == "POST":
            username = request.form["r_username"]
            password = request.form["r_password"]
            if not validate_username(username):
                return "Invalid username"
            if not validate_password(password):
                return "Invalid password"
        else:
            return "Invalid request"
    except Exception as e:
        logger.error("Invalid request: " + str(e))
        return "Invalid request"

    try:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Failed to register user."

        user_type = "user"
        new_user = User(
            username=username,
            password_hash=hash_password(password),
            user_type=user_type,
        )
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        logger.error("Error registering user: " + str(e))
        return "Error registering user"

    return "User registered successfully"


@app.route("/part1_vulnerable", methods=["GET", "POST"])
def part1_vulnerable():
    if "username" in session:
        return redirect(url_for("part1_logged_in"))

    if request.method == "GET":
        password = request.args.get("v_password")
        username = request.args.get("v_username")
        remember = request.args.get("v_remember")
    else:
        password = request.form["v_password"]
        username = request.form["v_username"]
        remember = request.form["v_remember"]

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = '" + username + "'")
        user = cur.fetchone()

        if user is None:
            return "Failed to login"

        valid_pass = verify_password(user[1], password)
        query = (
            "SELECT * FROM users WHERE username = '"
            + username
            + "' AND 'True' = '"
            + str(valid_pass)
            + "'"
        )
        logger.info(query)
        cur.execute(query)
        row = cur.fetchone()

        if row is None:
            return "Failed to login"

        if remember == "on":
            session["username"] = username
            session["password"] = password
            session["user_type"] = user[2]
            session.permanent = True
        else:
            session.clear()

        return render_template("part1_logged_in.html", username=username)

    except Exception as e:
        logger.error("Error logging in: " + str(e))
        return "Error logging in"
    finally:
        if conn:
            conn.close()


@app.route("/part1_correct", methods=["POST"])
def part1_correct():
    if "username" in session and "user_type" in session:
        return redirect(url_for("part1_logged_in"))
    try:
        if request.method == "POST":
            username = request.form["c_username"]
            password = request.form["c_password"]
            remember = request.form["c_remember"]

            if not validate_username(username):
                return "Invalid username"
            if not validate_password(password):
                return "Invalid password"
        else:
            return "Invalid request"

    except Exception as e:
        logger.error("Invalid request: " + str(e))
        return "Invalid request"

    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
            return "Failed to login"

        valid_pass = verify_password(user.password_hash, password)
        if not valid_pass:
            return "Failed to login"

        if remember == "on":
            session.clear()
            session["username"] = user.username
            session["user_type"] = user.user_type
            session.permanent = True
        else:
            session.clear()

        return render_template("part1_logged_in.html", username=username)

    except Exception as e:
        logger.error("Error logging in: " + str(e))
        return "Error logging in"


@app.route("/part2.html", methods=["GET"])
def part2():
    if "username" not in session or "user_type" not in session:
        return redirect(url_for("login"))

    try:
        messages = Message.query.all()
    except Exception as e:
        logger.error("Error finding message: " + str(e))
        return "Error finding message"

    return render_template("part2.html", messages=messages)


@app.route("/part2_vulnerable", methods=["GET", "POST"])
def part2_vulnerable():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        text = request.args.get("v_text")
    else:
        text = request.form["v_text"]
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (author, message) VALUES ('Vulnerable', '"
            + text
            + "')"
        )
        conn.commit()

    except Exception as e:
        return "Error finding message"
    finally:
        if conn:
            conn.close()

    return redirect(url_for("part2"))


@app.route("/part2_correct", methods=["POST"])
def part2_correct():
    if "username" not in session or "user_type" not in session:
        return redirect(url_for("login"))

    try:
        if request.method == "POST":
            text = validate_text(request.form["c_text"])
        else:
            return "Invalid request"
        
    except Exception as e:
        logger.error("Invalid request: " + str(e))
        return "Invalid request"
    
    try:
        new_message = Message(author="Correct", message=text)
        db.session.add(new_message)
        db.session.commit()

    except Exception as e:
        logger.error("Error sending message: " + str(e))
        return "Error sending message"

    return redirect(url_for("part2"))


@app.route("/part3.html", methods=["GET"])
def part3():
    if "username" not in session or "user_type" not in session:
        return redirect(url_for("login"))

    return render_template("part3.html", books=[])


@app.route("/part3_vulnerable", methods=["GET", "POST"])
def part3_vulnerable():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        # do not check if the values are valid or not
        name = request.args.get("v_name")
        author = request.args.get("v_author")
        category_id = request.args.get("v_category_id")
        pricemin = request.args.get("v_pricemin")
        pricemax = request.args.get("v_pricemax")

        # advanced search for text in the database
        search_input = request.args.get("v_search_input")
        search_field = request.args.get("v_search_field")
        radio_match = request.args.get("v_radio_match")

        sp_d = request.args.get("v_sp_d")
        sp_date_range = request.args.get("v_sp_date_range")
        sp_start_month = request.args.get("v_sp_start_month")
        sp_start_day = request.args.get("v_sp_start_day")
        sp_start_year = request.args.get("v_sp_start_year")
        sp_end_month = request.args.get("v_sp_end_month")
        sp_end_day = request.args.get("v_sp_end_day")
        sp_end_year = request.args.get("v_sp_end_year")

        sp_c = request.args.get("v_sp_c")
        sp_m = request.args.get("v_sp_m")
        sp_s = request.args.get("v_sp_s")

    else:
        name = request.form["v_name"]
        author = request.form["v_author"]
        category_id = request.form["v_category_id"]
        pricemin = request.form["v_pricemin"]
        pricemax = request.form["v_pricemax"]

        search_input = request.form["v_search_input"]
        search_field = request.form["v_search_field"]
        radio_match = request.form["v_radio_match"]

        sp_d = request.form["v_sp_d"]
        sp_date_range = request.form["v_sp_date_range"]
        sp_start_month = request.form["v_sp_start_month"]
        sp_start_day = request.form["v_sp_start_day"]
        sp_start_year = request.form["v_sp_start_year"]
        sp_end_month = request.form["v_sp_end_month"]
        sp_end_day = request.form["v_sp_end_day"]
        sp_end_year = request.form["v_sp_end_year"]

        sp_c = request.form["v_sp_c"]
        sp_m = request.form["v_sp_m"]
        sp_s = request.form["v_sp_s"]

    try:
        query = Book.query

        if name:
            query = query.filter(Book.title.like("%" + name + "%"))
        if author:
            query = query.filter(Book.authors.like("%" + author + "%"))
        if category_id:
            query = query.filter(Book.category.like("%" + category_id + "%"))
        if pricemin:
            query = query.filter(Book.price >= pricemin)
        if pricemax:
            query = query.filter(Book.price <= pricemax)

        if search_input and search_field != "any" and radio_match:
            if radio_match == "phrase":
                query = SearchLogic.v_search_phrase(query, search_field, search_input)
            elif radio_match == "all":
                query = SearchLogic.v_search_all(query, search_field, search_input)
            elif radio_match == "any":
                query = SearchLogic.v_search_any(query, search_field, search_input)

        elif search_input and search_field == "any" and radio_match:
            if radio_match == "phrase":
                query = SearchLogic.v_search_any_field_phrase(query, search_input)
            elif radio_match == "all":
                query = SearchLogic.v_search_any_field_all(query, search_input)
            elif radio_match == "any":
                query = SearchLogic.v_search_any_field_any(query, search_input)

        if sp_d == "custom":
            if sp_date_range:
                if sp_date_range == "-1":
                    pass
                else:
                    query = query.filter(
                        Book.book_date
                        >= datetime.datetime.now()
                        - datetime.timedelta(days=int(sp_date_range))
                    )
        elif sp_d == "specific":
            try:
                if sp_start_month and sp_start_day and sp_start_year:
                    start_date = datetime.datetime(
                        int(sp_start_year), int(sp_start_month), int(sp_start_day)
                    )
                    if sp_end_month and sp_end_day and sp_end_year:
                        end_date = datetime.datetime(
                            int(sp_end_year), int(sp_end_month), int(sp_end_day)
                        )
                        query = query.filter(
                            Book.book_date >= start_date, Book.book_date <= end_date
                        )
                    else:
                        return "Invalid end date"
                else:
                    return "Invalid start date"
            except ValueError:
                return "Invalid date format, please use YYYY-MM-DD"

        if sp_m == "0":
            query = query.with_entities(
                Book.title, Book.authors, Book.category, Book.price, Book.book_date
            )

        if sp_s == "1":
            query = query.order_by(Book.book_date.desc())
        elif sp_s == "0":
            query = query.order_by(Book.recomendation.desc())

        # do not check if sp_c is a whitelisted value
        if sp_c:
            query = query.limit(int(sp_c))

        books = query.all()

        return render_template("part3.html", books=books)

    except Exception as e:
        logger.error("Error finding books: " + str(e))
        return "Error finding books"


@app.route("/part3_correct", methods=["GET"])
def part3_correct():
    if "username" not in session or "user_type" not in session:
        return redirect(url_for("login"))

    try:
        if request.method == "GET":
            name = request.args.get("c_name", type=str).strip()
            author = request.args.get("c_author", type=str).strip()
            category_id = request.args.get("c_category_id", type=str).strip()
            pricemin = request.args.get("c_pricemin", type=float)
            pricemax = request.args.get("c_pricemax", type=float)

            search_input = request.args.get("c_search_input", type=str).strip()
            search_field = request.args.get("c_search_field", type=str).strip()
            radio_match = request.args.get("c_radio_match", type=str).strip()

            sp_d = request.args.get("c_sp_d", type=str).strip()
            sp_date_range = request.args.get("c_sp_date_range", type=int)
            sp_start_month = request.args.get("c_sp_start_month", type=int)
            sp_start_day = request.args.get("c_sp_start_day", type=int)
            sp_start_year = request.args.get("c_sp_start_year", type=int)
            sp_end_month = request.args.get("c_sp_end_month", type=int)
            sp_end_day = request.args.get("c_sp_end_day", type=int)
            sp_end_year = request.args.get("c_sp_end_year", type=int)

            sp_c = request.args.get("c_sp_c", type=int)
            sp_m = request.args.get("c_sp_m", type=str)
            sp_s = request.args.get("c_sp_s", type=int)
        else:
            return "Invalid request"
    
    except Exception as e:
                logger.error("Invalid request: " + str(e))
                return "Invalid request"

    try:
        query = Book.query

        if name:
            query = query.filter(Book.title.like("%" + name + "%"))
        if author:
            query = query.filter(Book.authors.like("%" + author + "%"))
        if category_id:
            query = query.filter(Book.category.like("%" + category_id + "%"))
        if pricemin:
            query = query.filter(Book.price >= pricemin)
        if pricemax:
            query = query.filter(Book.price <= pricemax)

        if search_input and search_field != "any" and radio_match:
            if radio_match == "phrase":
                query = SearchLogic.search_phrase(query, search_field, search_input)
            elif radio_match == "all":
                query = SearchLogic.search_all(query, search_field, search_input)
            elif radio_match == "any":
                query = SearchLogic.search_any(query, search_field, search_input)

        elif search_input and search_field == "any" and radio_match:
            if radio_match == "phrase":
                query = SearchLogic.search_any_field_phrase(query, search_input)
            elif radio_match == "all":
                query = SearchLogic.search_any_field_all(query, search_input)
            elif radio_match == "any":
                query = SearchLogic.search_any_field_any(query, search_input)

        if sp_d == "custom":
            if sp_date_range:
                if sp_date_range == -1:
                    pass
                else:
                    query = query.filter(
                        Book.book_date
                        >= datetime.datetime.now()
                        - datetime.timedelta(days=sp_date_range)
                    )
        elif sp_d == "specific":
            try:
                if sp_start_month and sp_start_day and sp_start_year:
                    start_date = datetime.datetime(
                        sp_start_year, sp_start_month, sp_start_day
                    )
                    if sp_end_month and sp_end_day and sp_end_year:
                        end_date = datetime.datetime(
                            sp_end_year, sp_end_month, sp_end_day
                        )
                        query = query.filter(
                            Book.book_date >= start_date, Book.book_date <= end_date
                        )
                    else:
                        return "Invalid end date"
                else:
                    return "Invalid start date"
            except ValueError:
                return "Invalid date format, please use YYYY-MM-DD"

        if sp_m == 0:
            query = query.with_entities(
                Book.title, Book.authors, Book.category, Book.price, Book.book_date
            )

        if sp_s:
            query = query.order_by(Book.book_date.desc())
        else:
            query = query.order_by(Book.recomendation.desc())

        if sp_c and sp_c in [5, 10, 25, 50, 100]:
            query = query.limit(sp_c)

        books = query.all()

        for book in books:
            if not isinstance(book, Book):
                return "Error finding books"

        return render_template("part3.html", books=books)

    except Exception as e:
        logger.error("Error finding books: " + str(e))
        return "Error finding books"


##########################################################
## DATABASE ACCESS FOR VULNERABLE PARTS
##########################################################

# The creadentials are hardcoded, bad practice.


def get_db():
    db = psycopg2.connect(
        user="ddss-database-assignment-2",
        password="ddss-database-assignment-2",
        host="db",
        port="5432",
        database="ddss-database-assignment-2",
    )

    return db


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s:  %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("\n---------------------\n\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
