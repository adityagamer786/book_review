import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
    #Redirect user to dashboard if signed in otherwise to register
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

    return render_template('login.html', message="Successfully registered. Now Sign In")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method != POST:
        return render_template('login.html', message="Please fill the form")
    username = request.form.get("username")
    password = request.form.get("password")

    user = db.execute("SELECT id, password, name FROM users WHERE username = :username", {"username": username}).fetchone()

    if user None:
        return render_template('login.html', message="Please enter correct username/password")

    password_hash = user.password
    user_id = user.id
    name = user.name

    if bcrypt.check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["name"] = name
        return redirect(url_for('dashboard', title="Dashboard", name=session["name"]))
