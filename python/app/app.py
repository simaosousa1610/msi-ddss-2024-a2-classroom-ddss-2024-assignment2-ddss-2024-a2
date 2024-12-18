#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from flask import Flask, render_template, g, request, redirect, url_for,  make_response, session, redirect, url_for
import logging, psycopg2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from flask_wtf import CSRFProtect 

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

csrf = CSRFProtect(app) 

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
    return bool(re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%^&+=.,]).{8,}$', password))

def validate_username(username):
    return bool(re.search(r'^[a-zA-Z0-9]{3,}$', username))

@app.route("/")
def home():
    return render_template("index.html");

@app.route("/part1.html", methods=['GET'])
def login():
    if 'username' in session and 'password' in session:
        return redirect(url_for('part1_logged_in'))

    return render_template("part1.html")

@app.route("/part1_logged_in", methods=['GET'])
def part1_logged_in():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('part1.html'))

    return render_template("part1_logged_in.html", username=session['username'])

@app.route("/part1_logout", methods=['GET', 'POST'])
def part1_logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))

@app.route("/part1_register", methods=['POST'])
def part1_register():
    
    if request.method == 'POST':
        username = request.form['r_username']
        password = request.form['r_password']
        if not validate_username(username):
            return "Invalid username"
        if not validate_password(password):
            return "Invalid password"
    else:
        return "Invalid request"
        
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        statement = "SELECT * FROM users WHERE username = %s"
        values = (username,)
        cur.execute(statement, values)

        if cur.rowcount > 0:
            return "Failed to register user."
        
        user_type = "user"

        statement = "INSERT INTO users (username, password_hash, user_type) VALUES (%s, %s, %s)"
        values = (username, hash_password(password), user_type)
        cur.execute(statement, values) 

        conn.commit()

    except Exception as e:
        logger.error("Error registering user: " + str(e))
        return "Error registering user"
    finally:
        if conn:
            conn.close()

    return "User registered successfully"


@app.route("/part1_vulnerable", methods=['GET', 'POST'])
def part1_vulnerable():
    logger.info("---- part1_vulnerable ----")

    if request.method == 'GET':
        password = request.args.get('v_password')
        username = request.args.get('v_username')
        remember = request.args.get('v_remember')
    else:
        password = request.form['v_password']
        username = request.form['v_username']
        remember = request.form['v_remember']

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = '" + username + "'")
        user = cur.fetchone()

        if user is None:
            return "Failed to login"

        valid_pass = verify_password(user[1], password)
        query = "SELECT * FROM users WHERE username = '" + username + "' AND 'True' = '" + str(valid_pass) + "'"
        logger.info(query)
        cur.execute(query)
        row = cur.fetchone()

        if row is None:
            return "Failed to login"
        
        if remember == "on":
            session['username'] = username
            session['password'] = password
            session.permanent = True
        
        return render_template("part1_logged_in.html", username=username)
        
        
    except Exception as e:
        logger.error("Error logging in: " + str(e))
        return "Error logging in"
    finally:
        if conn:
            conn.close()


@app.route("/part1_correct", methods=['POST'])
def part1_correct():
    try:
        if request.method == 'POST':
            password = request.form['c_password']
            username = request.form['c_username']
            remember = request.form.get('c_remember', 'off')

            if not validate_username(username):
                return "Invalid username"
            if not validate_password(password):
                return "Invalid password"
        else:
            return "Invalid request"
        
    except Exception as e:
        logger.error("Invalid request: " + str(e))
        return "Invalid request"

    conn = None

    try:
        conn = get_db()
        cur = conn.cursor()
        
        statement = "SELECT * FROM users WHERE username = %s"
        values = (username,)
        cur.execute(statement, values)
        row = cur.fetchone()
        password_hash = row[1]
        user_type = row[2]

        if not row or not verify_password(password_hash, password):
            return "Failed to login"
        
        if remember == "on":
            session['username'] = username
            session['user_type'] = user_type
            session.permanent = False
        
        return render_template("part1_logged_in.html", username=username)
        
    except Exception as e:
        logger.error("Error logging in: " + str(e))
        return "Error logging in"
    finally:
        if conn:
            conn.close()
        

@app.route("/part2.html", methods=['GET'])
def part2():
    if 'username' not in session or 'user_type' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages")
        messages = cur.fetchall()
    except Exception as e:
        logger.error("Error finding message: " + str(e))
        return "Error finding message"
    finally:
        if conn:
            conn.close()

    return render_template("part2.html", messages=messages)

@app.route("/part2_vulnerable", methods=['GET', 'POST'])
def part2_vulnerable():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        text = request.args.get('v_text')
    else:
        text = request.form['v_text']

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO messages (author, message) VALUES ('Vulnerable', '" + text + "')")

        conn.commit()
    
    except Exception as e:
        return "Error finding message"
    finally:
        if conn:
            conn.close()

    return redirect(url_for('part2'))


@app.route("/part2_correct", methods=['POST'])
def part2_correct():
    if 'username' not in session or 'user_type' not in session:
        return redirect(url_for('login'))

    try:
        if request.method == 'POST':
            text = request.form['c_text'].strip()
            if not text:
                return "Invalid message"
            
            if len(text) > 255:
                return "Message too long"
        else:
            return "Invalid request"
    except Exception as e:
        logger.error("Invalid request: " + str(e))
        return "Invalid request"

    try:
        conn = get_db()
        cur = conn.cursor()
        statement = "INSERT INTO messages (author, message) VALUES (%s, %s)"
        values = ('Correct', text)
        cur.execute(statement, values)
        conn.commit()
    
    except Exception as e:
        logger.error("Error finding message: " + str(e))
        return "Error finding message"
    finally:
        if conn:
            conn.close()

    return redirect(url_for('part2'))


@app.route("/part3.html", methods=['GET'])
def part3():
    if 'username' not in session or 'user_type' not in session:
        return redirect(url_for('login'))


    return render_template("part3.html");


@app.route("/part3_vulnerable", methods=['GET', 'POST'])
def part3_vulnerable():
    if 'username' not in session or 'user_type' not in session:
        return redirect(url_for('login'))

    return "/part3_vulnerable"


@app.route("/part3_correct", methods=['GET', 'POST'])
def part3_correct():
    

    return "/part3_correct"


@app.route("/demo", methods=['GET', 'POST'])
def demo():
    logger.info("\n DEMO \n");   

    conn = get_db()
    cur = conn.cursor()

    logger.info("---- users  ----")
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()

    for row in rows:
        logger.info(row)

    for row in rows:
        logger.info(row)

    logger.info("---- messages ----")
    cur.execute("SELECT * FROM messages")
    rows = cur.fetchall()
 
    for row in rows:
        logger.info(row)

    logger.info("---- books ----")
    cur.execute("SELECT * FROM books")
    rows = cur.fetchall()
 
    for row in rows:
        logger.info(row)

    conn.close ()
    logger.info("\n---------------------\n\n") 

    return "/demo"


##########################################################
## DATABASE ACCESS
##########################################################

def get_db():
    db = psycopg2.connect(user = "ddss-database-assignment-2",
                password = "ddss-database-assignment-2",
                host = "db",
                port = "5432",
                database = "ddss-database-assignment-2")
    return db





##########################################################
## MAIN
##########################################################
if __name__ == "__main__":
    logging.basicConfig(filename="log_file.log")

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger.info("\n---------------------\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)





