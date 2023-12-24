from flask import Flask,flash
from sqlalchemy import func,or_
from flask import Flask,render_template,request,redirect,url_for,session,flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from flask_login import login_required
from sqlalchemy.orm import load_only
from datetime import datetime
import json
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usercreds.sqlite3'
db.init_app(app)
app.secret_key='secret'
app.app_context().push()
db.create_all()
with open('templates/books.json', 'r') as json_file:
    books_data = json.load(json_file)
@app.route("/",methods=['GET','POST'])
def home():
    results=[]
    if request.method == 'POST':
        search_category = request.form.get('category')
        search_title = request.form.get('title')
        if search_category or search_title:
            results = Book.query.filter(or_(
                func.lower(Book.category).contains(search_category.lower()) if search_category else False,
                func.lower(Book.title).ilike(f"%{search_title.lower()}%") if search_title else False,
            )).all()
        else:
            results=Book.query.all()
    else:
        results=Book.query.all()
    return render_template('index.html',results=results)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pwd')
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['user_id']=user.id
            print(session)
            print("User ID set in session:", session['user_id'])  # Add this line for debugging
            return redirect(url_for('profile'))
        elif user:
            return render_template('login.html', message=2)  # Incorrect password
        else:
            return render_template('login.html', message=1)  # Incorrect username
    if 'user' in session:
        return redirect(url_for('profile'))
    return render_template('login.html') 
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pwd')
        email = request.form.get('email')
        userlist = [value[0] for value in Users.query.with_entities(Users.username).all()]
        if username not in userlist:
            hashed_password = generate_password_hash(password, method='sha256')
            user = Users(username=username, password=hashed_password, email=email)
            db.session.add(user)
            db.session.commit()
            return render_template('signup.html', message=2)
        return render_template('signup.html', message=0)
    return render_template('signup.html', message=1)
@app.route('/books',methods=['GET','POST'])
def books():
    books_data=Book.query.all()
    return render_template('books.html',books=books_data)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    books_data = Book.query.all()
    if request.method == 'POST':
        search_category = request.form.get('category')
        search_title = request.form.get('title')
        output = []
        for book in books_data:
            if search_category and search_category.lower() in book.category.lower():
                output.append(book)
            elif search_title and search_title.lower() in book.title.lower():
                output.append(book)
        return render_template('profile.html', results=output)
    return render_template('profile.html', results=books_data)
@app.route('/books-all',methods=['GET','POST'])
def books_all():
    books_data=Book.query.all()
    return render_template('books-all.html',books=books_data)
@app.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    if 'user' in session:
        user_id = session['user_id']
        book_id = request.form.get('id') 

        quantity = 1  # You can modify this based on user input

        # Check if the book is already in the cart
        existing_item = Cart.query.filter_by(user_id=user_id, book_id=book_id).first()

        # Check if the book exists
        book = Book.query.get(book_id)

        if book and book.bookcount >= quantity:
            # If the book is available, proceed to update the cart and bookcount
            if existing_item:
                # Update the quantity if the item is already in the cart
                existing_item.quantity += quantity
            else:
                # Add the item to the cart if it's not already there
                new_cart_item = Cart(user_id=user_id, book_id=book_id, quantity=quantity)
                db.session.add(new_cart_item)

            # Update the bookcount in the Book model
            book.bookcount -= quantity
            db.session.commit()

            flash('Book added to the cart successfully!', 'success')
        else:
            # If the book is not available, show a flash message
            flash('Sorry, the book is not available.', 'danger')

        # Redirect to the user's profile or wherever you want
        return redirect(url_for('profile'))
    else:
        # Handle the case where the user is not logged in
        return redirect(url_for('login'))

# Add a new route to display the cart contents
@app.route("/cart")
def view_cart():
    if 'user' in session:
        user_id = session['user_id']
        cart_items = (
            db.session.query(Cart, Book)
            .join(Book, Cart.book_id == Book.id)
            .filter(Cart.user_id == user_id)
            .all()
        )
        total_price = sum(cart_item.quantity * book.price for cart_item, book in cart_items)
        return render_template('cart.html', cart_items=cart_items,total_price=total_price)
    else:
        # Handle the case where the user is not logged in
        return redirect(url_for('login'))
@app.route("/update_cart", methods=["POST"])
def update_cart():
    if 'user' in session:
        user_id = session['user_id']
        cart_item_id = request.form.get("cart_item_id")
        action = request.form.get("action")

        # Retrieve the cart item
        cart_item = Cart.query.get(cart_item_id)

        if cart_item:
            # Update the quantity based on the action
            if action == "reduce" and cart_item.quantity > 1:
                cart_item.quantity -= 1
                book=Book.query.get(cart_item.book_id)
                book.bookcount+=1
                db.session.commit()

            elif action=="reduce" and cart_item.quantity==1:
                flash("Cannot reduce quantity further. If you want to remove the item, use the 'Delete' button.", "warning")
        return redirect(url_for('view_cart'))
    else:
        # Handle the case where the user is not logged in
        return redirect(url_for('login'))

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    if 'user' in session:
        user_id = session['user_id']
        cart_item_id = request.form.get("cart_item_id")

        # Retrieve the cart item
        cart_item = Cart.query.get(cart_item_id)

        if cart_item:
            book=Book.query.get(cart_item.book_id)
            book.bookcount+=cart_item.quantity
            # Delete the cart item
            db.session.delete(cart_item)
            db.session.commit()
            flash("Book deleted successfully")
        return redirect(url_for('view_cart'))
    else:
        # Handle the case where the user is not logged in
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        #session.pop('user_id')
        return redirect(url_for('home'))
## admin login side
@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        username=request.form.get('uname')
        password=request.form.get('pwd')
        if username=='admin' and password=='admin-password':
            session['ad-user']='admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('adminlogin.html', message=0)
    if 'ad-user' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('adminlogin.html')
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'ad-user' in session and session['ad-user']=='admin':
        if request.method == 'POST':
            title = request.form.get('title')
            category = request.form.get('category')
            authors = request.form.get('authors')
            thumbnail = request.form.get('thumbnail')
            pageCount = request.form.get('pageCount')
            bookcount = request.form.get('bookcount')
            publishdate = request.form.get('publishdate')
            price = request.form.get('price')
            new_book = Book(
            title=title,
            category=category,
            authors=authors,
            thumbnail=thumbnail,
            pageCount=pageCount,
            bookcount=bookcount,
            publishdate=publishdate,
            price=price
            )
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_UI.html')
    else:
        return render_template('adminlogin.html')
@app.route('/books_reg',methods=['GET','POST'])
def books_register_admin():
    if 'ad-user' in session and session['ad-user']=='admin':
        books=Book.query.all()
        total_books=sum(book.bookcount for book in books)
        unique_category=set(book.category for book in books)
        return render_template('books_reg_admin.html',books=books,total_books=total_books,unique_categories=unique_category)
    else:
        return render_template('adminlogin.html')
@app.route('/admin_logout',methods=['GET','POST'])
def admin_logout():
    if 'ad-user' in session:
        session.pop('ad-user')
        return redirect(url_for('home'))
if __name__=="__main__":
    app.run(debug=True)