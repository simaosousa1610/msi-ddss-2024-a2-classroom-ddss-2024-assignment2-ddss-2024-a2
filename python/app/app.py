#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g, request, redirect, url_for,  make_response
import logging, psycopg2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

app = Flask(__name__)


ph = PasswordHasher()

def hash_password(password):
    return ph.hash(password)

def verify_password(stored_hash, password):
    try:
        ph.verify(stored_hash, password)
        return True
    except VerifyMismatchError:
        return False


@app.route("/")
def home():
    return render_template("index.html");



@app.route("/part1.html", methods=['GET'])
def login():

    # anything needed to be done here?
    # get the username from the cookie and display it in the form
    username = request.cookies.get('username')

    if username is not None:
        return render_template("part1.html", username=username)

    return render_template("part1.html");


@app.route("/part1_register", methods=['GET', 'POST'])
# Register a new user according to best practices, without any vulnerabilities
def part1_register():
    logger.info("---- part1_register ----")

    if request.method == 'GET':
        password = request.args.get('r_password') 
        username = request.args.get('r_username') 
    else:
        password = request.form['r_password']
        username = request.form['r_username']

    try:
        conn = get_db()
        cur = conn.cursor()

        # Enforcing a secure password policy
        if len(password) < 8 or len(password) > 64:
            return "Password must be between 8 and 64 characters long"
        
        if not any(char.isdigit() for char in password):
            return "Password must contain at least one digit"
    
        if not any(char.isupper() for char in password):
            return "Password must contain at least one uppercase letter"
        
        if not any(char.islower() for char in password):
            return "Password must contain at least one lowercase letter"
        
        if not any(char in "!@#$%^&*()-+" for char in password):
            return "Password must contain at least one special character"

        # Check if user already exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))

        if cur.rowcount > 0:
            # User already exists            
            return "Failed to register user."
        
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hash_password(password))) 

        conn.commit()

    except Exception as e:
        logger.error("Error registering user: " + str(e))
        return "Error registering user"
    finally:
        conn.close()

    return "/part1_register"


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
        
        '''SQL Injection vulnerability'''
        cur.execute ("SELECT * FROM users WHERE username = '" + username + "'")
        row = cur.fetchone()
        if row is None:
            return "User does not exist"
        
        if not verify_password(row[1], password): 
            '''Oversharing of information, this could be used by an attacker to determine if a username is valid or not'''
            return "Wrong password"
        
        if remember == "on":
            '''
            Bad cookie handling
            -> Cookie is:   not signed or encrypted, so it can be easily manipulated
            ->              not set to be HttpOnly, so it can be accessed by JavaScript
            ->              not set to be Secure, so it can be sent over an unencrypted connection
            ->              not set to be SameSite, so it can be sent cross-site    
            '''
            resp = make_response("Successfully logged in")
            resp.set_cookie('username', username)
            return resp
        else:
            return "/part1_vulnerable"

    except Exception as e:
        logger.error("Error logging in: " + str(e))
        return "Error logging in"
    finally:
        conn.close()

@app.route("/part1_correct", methods=['GET', 'POST'])
def part1_correct():
    logger.info("---- part1_correct ----")

    if request.method == 'GET':
        password = request.args.get('c_password') 
        username = request.args.get('c_username') 
        remember = request.args.get('c_remember')

    else:
        password = request.form['c_password']
        username = request.form['c_username']
        remember = request.form['c_remember']
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Verify the password of the user
        query = "SELECT password_hash FROM users WHERE username = %s"
        cur.execute(query, (username,))
        row = cur.fetchone()
        if row is None:
            return "Failed to login"
        
        if not verify_password(row[0], password):
            return "Failed to login"
        
        if remember == "on":
            '''
            Set a secure, signed and encrypted cookie
            Set the cookie to be HttpOnly, so it can't be accessed by JavaScript
            Set the cookie to be Secure, so it can't be sent over an unencrypted connection
            Set the cookie to be SameSite, so it can't be sent cross-site
            '''
            resp = make_response("Successfully logged in")
            # Set the cookie to be signed and encrypted
            resp.set_cookie('username', username, secure=True, httponly=True, samesite='Strict')

            return resp
        else:
            return "/part1_correct"
        
    except Exception as e:
        logger.error("Error logging in: " + str(e))
        return "Error logging in"
    finally:
        conn.close()
        

@app.route("/part2.html", methods=['GET'])
def part2():



    return render_template("part2.html");


@app.route("/part2_vulnerable", methods=['GET', 'POST'])
def part2_vulnerable():
    
   

    return "/part2_vulnerable"


@app.route("/part2_correct", methods=['GET', 'POST'])
def part2_correct():
    

    return "/part2_correct"






@app.route("/part3.html", methods=['GET'])
def part3():


    return render_template("part3.html");


@app.route("/part3_vulnerable", methods=['GET', 'POST'])
def part3_vulnerable():
    
   

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





