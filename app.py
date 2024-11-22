from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///closet.db")

#users table
    #id: user's id
    #username
    #password: hashed
    #college (one of 14)Yale residential colleges
    #name

#inquries table
    #id: inquiry_id
    #user_id: id of the poster
    #accepted: "yes" or  "no" (default is no)
    #time_published: YYYY-MM-DD HH:MI:SS
    #request: user's reason
    #exp_date: YYYY-MM-DD

#tags table
    #inquiry_id
    #tags: anything from style to size

#interactions
    #inquiry_id
    #status: text
    #lender_id: user_id of lender

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Refering to login.html: username input should have the name as "username", password input should have the name as "password", should be a submitted form
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Query users database to check if someone has that username
        person = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )

        # Ensure username only belongs to one user and password is correct
        if len(person) != 1 or not check_password_hash(
            person[0]["password"], password
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = person[0]["id"]

        # Redirect user to feed page
        return redirect("/feed")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

'''@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/about")'''


'''#Referring to register.html: username=username, password=password, email=email, college=college (drop down with ResCos), name=name, should be submitted as a form
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 400)

        # Ensure username was submitted
        elif not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure email was submitted
        elif not request.form.get("email"):
            return apology("must provide email,", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password again", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        college = request.form.get("college")
        password = generate_password_hash(request.form.get("password"))

        # Checks if user already exists, redirects to login
        try:
            db.execute(
                "INSERT INTO users (name, username, email, college, password) VALUES (?, ?, ?, ?, ?)",
                name, username, email, college, password)
        except ValueError:
            return apology("username already exists.", 400)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

#References feed.html.'''

@app.route("/feed", methods=["GET", "POST"])
@login_required
def feed():
    # User reached route via POST (aka they create an inquiry)
    #if request.method == "POST":

    return render_template("feed.html")

