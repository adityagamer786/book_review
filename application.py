import os

import requests
import json
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    ####################################
    #Redirect user to dashboard if logged in otherwise to register
    if session.get("user_id") is None:
        return render_template('register.html')
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    ####################################
    #Redirect user to register if made GET request
    if request.method != 'POST':
        return render_template('register.html', message="Please fill the form")

    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')

    #Check for invalid entry
    if ( len(name) == 0 or len(username) == 0 or len(password) == 0):
        return render_template("register.html", message="Please fill all credentails")

    #Check if username already exists
    if (db.execute("SELECT username FROM users WHERE username = :username", {"username": username})).rowcount != 0:
        return render_template("register.html", message="Username already taken")

    password_hash = bcrypt.generate_password_hash(password).decode()
    db.execute("INSERT INTO users(username, password, name) VALUES)(:username, :password, :name)", {"username": username, "password": password_hash, "name": name})
    db.commit()

    return render_template('login.html', message="Successfully registered. Now Log In")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method != POST:
        return render_template('login.html', message="Please fill the form")
    username = request.form.get("username")
    password = request.form.get("password")

    user = db.execute("SELECT id, password, name FROM users WHERE username = :username", {"username": username}).fetchone()

    if user is None:
        return render_template('login.html', message="Please enter correct username/password")

    password_hash = user.password
    user_id = user.id
    name = user.name

    if bcrypt.check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["name"] = name
        return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if session.get("user_id") is not None:
        return render_template('dashboard.html', name=session["name"])
    else:
        return render_template('login.html', message="Please login first")

@app.route("/books")
def results():
    isbn = request.form.get("isbn")
    author = request.form.get("author")
    title = request.form.get("title")

    books = db.execute("SELECT * FROM books WHERE LOWER(isbn) LIKE :isbn AND LOWER(title) LIKE :title AND LOWER(author) LIKE :author", {"isbn": f"%{isbn}%", "title": f"%{title}%", "author": {f"%{author}%"}}).fetchall()

    return render_template('results.html', books=books)

@app.route("/book/<int:book_id>")
def bookDetail(book_id):
    if session.get("user_id") is None:
        return render_template('login.html', message="Please log in first")

    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()

    reviews = db.execute("SELECT review, rating, name FROM reviews JOIN users on reviews.user_id = users.id WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    already_reviewed = db.execute("SELECT * FROM reviews WHERE book_id = :book_id and user_id = :user_id", {"user_id": user_id}).rowcount >= 1

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("API_KEY"), "isbn": book.isbn}).json()

    return render_template('book.html', book = book, res=res['books'][0], reviews=reviews, already_reviewed=already_reviewed)
