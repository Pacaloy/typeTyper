import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///typeTyper.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        users = db.execute("SELECT * FROM users;")

        # Ensure username does not exist
        for i in range(len(users)):
            if users[i]["username"] == username:
                return apology("username already exists", 400)

        # Check if password and confirmation matches
        if password != confirmation:
            return apology("passwords do not match", 400)

        isAlphaNumeric = False
        numCount = 0

        for i in range(len(password)):
            if password[i] == "0" or password[i] == "1" or password[i] == "2" or password[i] == "3" or password[i] == "4" or password[i] == "5" or password[i] == "6" or password[i] == "7" or password[i] == "8" or password[i] == "9":
                isAlphaNumeric = True
                numCount = numCount + 1

        if not isAlphaNumeric or numCount == len(password):
            return apology("password should contain letters and numbers", 400)

          # Insert new user registration
        db.execute("INSERT INTO users (username, hash) VALUES (?,?);", username, generate_password_hash(password))

        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    """Submit score"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure score was submitted
        if not request.form.get("result"):
            return apology("missing result", 400)

        result = request.form.get("result")
        date = datetime.now()

        # Record result
        db.execute("INSERT INTO stats (user_id, result, date) VALUES (?, ?, ?);", session["user_id"], result, date)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


@app.route("/stats")
@login_required
def stats():
    """Show user stats"""

    results = db.execute("SELECT users.username, stats.result, stats.date FROM stats JOIN users ON users.id = stats.user_id WHERE stats.user_id = ? ORDER BY stats.date DESC;", session["user_id"])

    return render_template("stats.html", results=results)