from flask import Flask
from flask import Flask,render_template,request,redirect,url_for,session,flash
from models import *
from flask_oauthlib.client import OAuth
from flask_login import login_required
from sqlalchemy.orm import load_only

import json
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usercreds.sqlite3'
db.init_app(app)
app.secret_key='secret'
app.app_context().push()
def init_user_cart():
    if 'user_books' not in session:
        session['user_books'] = []
db.create_all()
with open('templates/books.json', 'r') as json_file:
    books_data = json.load(json_file)

@app.route("/",methods=['GET','POST'])
def home():
    if request.method == 'POST':
        search_category = request.form.get('category')
        search_title = request.form.get('title')
        results = []
        for book in books_data:
            if search_category and search_category.lower() in book['category'].lower():
                results.append(book)
            elif search_title and search_title.lower() in book['title'].lower():
                results.append(book)
        return render_template('index.html', results=results)
    return render_template('index.html', results=books_data)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('uname')
        password=request.form.get('pwd')
        user=Users.query.filter_by(username=username,password=password).first()
        if user:
            session['user']=user.username
            book_id=request.form.get('book_id')
            user_cart=UserBooks.query.filter_by(user_id=user.username).first()
            if user_cart and user_cart.book_id:
                cart_items = list(map(int, user_cart.book_id.split()))  # Split and convert to integers
                session['user_books'] = cart_items

            return redirect(url_for('profile'))
        else:
            return render_template('login.html',message=0)
    return render_template('login.html',message=1)


@app.route('/signup',methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        username=request.form.get('uname')
        password=request.form.get('pwd')
        #name=request.form.get('name')
        email=request.form.get('email')
        user=Users(username=username,password=password,email=email)
        userlist=[value[0] for value in Users.query.with_entities(Users.username).all()]
        if user.username not in userlist:
            db.session.add(user)
            db.session.commit()
            return render_template('signup.html',message=2)
        return render_template('signup.html',message=0)
    return render_template('signup.html',message=1)
@app.route('/books',methods=['GET','POST'])
def books():
    return render_template('books.html',books=books_data)
@app.route('/profile',methods=['GET','POST'])
def profile():
    if request.method == 'POST':
        search_category = request.form.get('category')
        search_title = request.form.get('title')
        output= []
        for book in books_data:
            if search_category and search_category.lower() in book['category'].lower():
                output.append(book)
            elif search_title and search_title.lower() in book['title'].lower():
                output.append(book)
        return render_template('profile.html', results=output)
    return render_template('profile.html', results=books_data)
@app.route('/books-all',methods=['GET','POST'])
def books_all():
    return render_template('books-all.html',books=books_data)
"""@app.route('/add', methods=['GET', 'POST'])
def add():
    user_id = session.get('user')
    if not user_id:
        return redirect(url_for('login'))
    book_ids = request.form.getlist('id')
    #if not book_ids:
    #    message = "No books are selected"
    '''if len(book_ids) != len(set(book_ids)):
        message = "Duplicate book IDs are not allowed" '''
    book_ids_str =''.join(book_ids)
    user_cart = UserBooks.query.filter_by(user_id=user_id).first()
    if user_cart:
        if user_cart.bookid:
            user_cart.bookid += f' {book_ids_str}'  # Separate with a space
        else:
            user_cart.bookid = book_ids_str
    else:
        user_cart = UserBooks(user_id=user_id, bookid=book_ids_str)
    db.session.add(user_cart)
    db.session.commit()
    return redirect(url_for('profile'))"""
@app.route('/add', methods=['POST'])
def add():
    user_id = session.get('user')
    if not user_id:
        return redirect(url_for('login'))
    
    book_ids = request.form.getlist('id')
    session_cart = session.get('user_books', [])
    user_cart = UserBooks.query.filter_by(user_id=user_id).first()
    
    # Ensure that only unique book IDs are stored in the session cart
    for book_id in book_ids:
        book_id_int = int(book_id)
        if book_id_int not in session_cart:
            session_cart.append(book_id_int)
        # Check if the book ID is already in the database cart
        if user_cart and user_cart.book_id:
            cart_book_ids = [int(id) for id in str(user_cart.book_id).split()]
            if book_id_int not in cart_book_ids:
                cart_book_ids.append(book_id_int)
                user_cart.book_id = ' '.join(map(str, cart_book_ids))
        elif user_cart:
            user_cart.book_id = str(book_id_int)
        else:
            user_cart = UserBooks(user_id=user_id, book_id=str(book_id_int))

    # Update the session-based cart
    session['user_books'] = session_cart
    
    db.session.add(user_cart)
    db.session.commit()
    
    return redirect(url_for('profile'))


with open('templates/books.json', 'r') as json_file:
    books_data = json.load(json_file)

'''@app.route('/cart', methods=['GET', 'POST'])
def cart():
    user_id = session.get('user')    
    book_tuples = UserBooks.query.filter_by(user_id=user_id).with_entities(UserBooks.bookid).all()
    book_ids = [int(id) for tup in book_tuples for id in tup[0].split()]
    unique_book_ids = set(book_ids)
    unique_book_ids_list = list(unique_book_ids)
    book_details = []
    for book_id in unique_book_ids_list:
        for book_info in books_data:
            if book_info['_id'] == book_id:
                book_details.append(book_info)

    if request.method == "POST":
        book_id_remove = int(request.form['remove_id'])
        if book_id_remove in unique_book_ids_list:
            unique_book_ids_list.remove(book_id_remove)
            UserBooks.query.filter_by(user_id=user_id, bookid=str(book_id_remove)).delete()
            db.session.commit()
    return render_template('cart.html', results=book_details, c_b=len(book_details))'''
@app.route('/cart',methods=['GET','POST'])
def cart():
    user_d=session.get('user')
    session_cart=session.get('user_books',[])
    cart_items=[]
    for book_id in session_cart:
        for book_info in books_data:
            if book_info['_id']==book_id:
                cart_items.append(book_info)

    if request.method=='POST':
        book_id_remove=int(request.form['remove_id'])
        if book_id_remove in session_cart:
            session_cart.remove(book_id_remove)
    session['user_books']=session_cart
    return render_template('cart.html',results=cart_items,c_b=len(cart_items))

'''@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user',None)
        return redirect(url_for('home'))'''
@app.route('/logout')
def logout():
    if 'user' in session:
        user_id = session['user']
        session_cart = session.get('user_books', [])
        user_cart = UserBooks.query.filter_by(user_id=user_id).first()

        if user_cart:
            # Combine the existing book IDs in the database with the session cart
            existing_book_ids = user_cart.book_id.split() if user_cart.book_id else []
            
            # Remove deleted books from the existing book IDs
            updated_book_ids = [book_id for book_id in existing_book_ids if book_id not in session_cart]
            
            user_cart.book_id = ' '.join(map(str, updated_book_ids))
        else:
            # If there's no existing cart in the database, use the session cart
            user_cart = UserBooks(user_id=user_id, book_id=' '.join(map(str, session_cart)))

        db.session.add(user_cart)
        db.session.commit()

        # Clear the session-based cart after updating the database
        session.pop('user_books', None)
        session.pop('user', None)
        return redirect(url_for('home'))


if __name__=="__main__":
    app.run(debug=True)