from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Users(db.Model):
    username=db.Column(db.String(50),primary_key=True)
    password=db.Column(db.String(50),nullable=False)
    #name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False)

class UserBooks(db.Model):
    __tablename__ = 'user_books'

    user_id = db.Column(db.String(50), db.ForeignKey('users.username'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)

    user = db.relationship('Users', backref=db.backref('user_books', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('user_books', lazy='dynamic'))

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    # Other book attributes like title, author, etc.
    title=db.Column(db.String(50),nullable=False)
    category=db.Column(db.String(50),nullable=False)
    count=db.Column(db.Integer,nullable=False)
    