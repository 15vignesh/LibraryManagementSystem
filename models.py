from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    category = db.Column(db.String(100), nullable=False)
    authors = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))
    pageCount = db.Column(db.Integer)
    bookcount = db.Column(db.Integer)
    publishdate = db.Column(db.String(100))
    price = db.Column(db.Integer)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    user = db.relationship('Users', backref=db.backref('carts', lazy=True))
    book = db.relationship('Book', backref=db.backref('carts', lazy=True))