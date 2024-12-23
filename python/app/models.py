from db import db

# CREATE TABLE users (
#     username        VARCHAR( 32)     primary key,
#     password_hash   TEXT             NOT NULL,
#     user_type       VARCHAR( 16)     NOT NULL
# );


# CREATE TABLE messages (
#     message_id  SERIAL PRIMARY KEY,
#     author      VARCHAR( 16)   ,
#     message     VARCHAR(256)    NOT NULL
# );

# CREATE TABLE books (
#     book_id         SERIAL PRIMARY KEY,
#     title           VARCHAR(128),
#     authors         VARCHAR(256),
#     category        VARCHAR(128),
#     price           NUMERIC(8,2),
#     book_date       DATE,
#     description     VARCHAR(1024),
#     keywords        VARCHAR(256),
#     notes           VARCHAR(256),
#     recomendation   INTEGER
# );

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(32), primary_key=True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(16))

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    authors = db.Column(db.String(256))
    category = db.Column(db.String(128))
    price = db.Column(db.Numeric(8,2))
    book_date = db.Column(db.Date)
    description = db.Column(db.String(1024))
    keywords = db.Column(db.String(256))
    notes = db.Column(db.String(256))
    recomendation = db.Column(db.Integer)

class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(16))
    message = db.Column(db.String(256))