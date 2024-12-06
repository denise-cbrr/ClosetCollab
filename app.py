import sqlite3
import os
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required

#Tables:
#users table
    #id: user's id
    #username (unique)
    #password: hashed
    #college (one of 14) Yale residential colleges
    #name

#inquiries table
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
    #status: text (delivered, received, etc.)
    #lender_id: user_id of lender

# Configure application
app = Flask(__name__)

# Folder where uploaded images will be stored
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
# Function to get the database connection
def get_db():
    """Opens a new database connection if one doesn't exist"""
    if 'db' not in g:
        g.db = sqlite3.connect('closet.db')
        g.db.row_factory = sqlite3.Row  # Allows access to columns by name
    return g.db

# Function to close the database connection
@app.teardown_appcontext
def close_db(exception):
    """Closes the database connection at the end of the request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Renders index.html, a page about our site with buttons to log in/register
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Ensures user login is valid
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
        db = get_db()  # Use the database connection from g

        # fetchone fetches the first row of the results
        person = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        # Ensure username only belongs to one user and password is correct
        if person is None or not check_password_hash(person["password"], password):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = person["id"]

        # Redirect user to feed page
        return redirect("/feed")

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
        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        college = request.form.get("college")
        password = generate_password_hash(request.form.get("password"))

        # Ensure name was submitted
        if not name:
            return apology("must provide name", 400)

        # Ensure email was submitted
        elif not email:
            return apology("must provide email,", 400)
        
        # Ensure username was submitted
        elif not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must validate password", 400)

        # Checks that both password inputs are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        
        # Checks if user's username is valid (unique); if it is, inserts a new user entry into user table
        try:
            db = get_db()  # Use the database connection from g

            db.execute(
                "INSERT INTO users (name, email, username, college, password) VALUES (?, ?, ?, ?, ?)",
                (name, email, username, college, password)
            )
            db.commit()

        except sqlite3.IntegrityError:
            return apology("username already exists.", 400)

        # Redirect user to index page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
@app.route("/feed", methods=["GET", "POST"])
def feed():
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        userRequest = request.form.get("userRequest")
        tags_list = request.form.getlist("style")   # Creates a list from the style tags
        # Extends list to include size and item, puts "None" if item left blank
        tags_list.extend(filter(None, [request.form.get("size"), request.form.get("item")]))    
        expirationDate = request.form.get("expirationDate")
        curUser = session["user_id"]
        
        db = get_db()  # Use the database connection from g
        db.execute(
            "INSERT INTO inquiries (request, exp_date, user_id) VALUES (?, ?, ?)",
            (userRequest, expirationDate, curUser)
        )
        
        inquiry_id = db.execute(
            "SELECT id FROM inquiries ORDER BY id DESC LIMIT 1"
        ).fetchone()[0] 

        for tag in tags_list:
            db.execute(
                "INSERT INTO tags (inquiry_id, tag) VALUES (?, ?)",
                (inquiry_id, tag)
            )
        db.commit()
        
        db = get_db()
        results = db.execute("""SELECT users.name, users.username, users.college, inquiries.*, 
                             GROUP_CONCAT(tags.tag, ', ') AS tags FROM users 
                             JOIN inquiries ON users.id = inquiries.user_id 
                             JOIN tags ON inquiries.id = tags.inquiry_id
                             WHERE inquiries.exp_date >= CURRENT_DATE 
                             GROUP BY inquiries.id 
                             ORDER BY inquiries.time_published DESC;""").fetchall()
        
        return render_template("feed.html", results=results)
    
    else:
        tags = request.args.getlist("styleFilter")
        size_filter = request.args.get("sizeFilter")
        type_filter = request.args.get("typeFilter")
        
        # creates the filtered feed if at least one filter is used
        if tags or size_filter or type_filter:
            
            # if there is a size filter, add to the tags list
            if size_filter:
                tags.append(size_filter)
                
            # if there is a type filter, add to the tags list
            if type_filter:
                tags.append(type_filter)
                
            tag_count = len(tags)
            placeholders = ', '.join(['?'] * len(tags))
            
            # placeholders will dynamically create the right amount of ? for each filter
            # IN () will return the inquiry_id of any inquiry with at least one of those tags
            # GROUP BY will group the inquiries by inqury_id so we deal with one row only
            # HAVING COUNT(DISTINCT t.tags) = ? will ensure that it only returns inquries with ALL tags
            # Order by helps make it so that the newest requests are shown first
            query = f"""
                SELECT users.name, users.username, users.college, inquiries.*, 
                GROUP_CONCAT(tags.tag, ', ') AS tags FROM inquiries 
                JOIN users ON users.id = inquiries.user_id 
                JOIN tags ON inquiries.id = tags.inquiry_id 
                WHERE tags.tag IN ({placeholders})
                AND inquiries.exp_date >= CURRENT_DATE 
                GROUP BY inquiries.id HAVING COUNT(DISTINCT tags.tag) = ? 
                ORDER BY inquiries.time_published DESC;"""
           
            db = get_db()
            results = db.execute(query, tags + [tag_count]).fetchall()
        
            # db.execute(f"SELECT i.*FROM inquiries i JOIN tags t ON i.id = t.inquiry_id WHERE t.tags IN ({tag_list}) 
            # GROUP BY i.id HAVING COUNT(DISTINCT t.tags) = {tag_count};")
            # Used code is better because it parametrizes and protects from SQL injection attacks
           
        else:
            # renders an unfiltered feed when no filters are used
            db = get_db()
            results = db.execute("""SELECT users.name, users.username, users.college, inquiries.*, 
                                 GROUP_CONCAT(tags.tag, ', ') AS tags FROM users 
                                 JOIN inquiries ON users.id = inquiries.user_id 
                                 JOIN tags ON inquiries.id = tags.inquiry_id
                                 WHERE inquiries.exp_date >= CURRENT_DATE 
                                 GROUP BY inquiries.id 
                                 ORDER BY inquiries.time_published DESC;""").fetchall()
        
        return render_template("feed.html", results=results)

@app.route("/inquiry/<int:inquiry_id>", methods=["GET", "POST"])
def inquiry(inquiry_id):
    db = get_db()
    inquiry = db.execute("""
       SELECT * FROM inquiries
        WHERE id = ?
    """, (inquiry_id,)).fetchone()

    if request.method == "POST":
        reply = request.form.get("replyResponse")
        curUser = session["user_id"]
        response = db.execute(
            "INSERT INTO responses (inquiry_id, prosp_Lender_id, reply) VALUES (?, ?, ?)",
            (inquiry_id, curUser, reply)
        )

    responses = db.execute(
        "SELECT responses.*, users.username AS lender_username FROM responses JOIN users ON responses.prosp_Lender_id = users.id WHERE responses.inquiry_id = ? ORDER BY responses.time_published DESC", (inquiry_id, )).fetchall();
        #"SELECT * FROM responses WHERE inquiry_id = ? ORDER BY time_published DESC", (inquiry_id,)
        #).fetchall()
    db.commit()

    return render_template("inquiry.html", responses=responses, inquiry = inquiry)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        
        if 'image' not in request.files:
            return apology ("No image uploaded", 400)
        
        file = request.files['image']
        
        if file.filename == '':
            return apology("No selected file.", 400)
        
        # saving the file to the server
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
        
    db = get_db()
    curUser = session["user_id"]
    inquiries = db.execute(
        "SELECT * FROM inquiries WHERE user_id = ?", (curUser, )).fetchall();
    return render_template("profile.html", inquiries = inquiries)


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route("/interactions")
def interactions():
    db = get_db()
    
    # this would work for the borrowing side (maybe we can return less information compared to feed?)
    # myInquiries = db.execute("SELECT users.name, users.username, users.college, inquiries.*, GROUP_CONCAT(tags.tag) AS tags FROM users JOIN inquiries ON users.id = inquiries.user_id JOIN tags ON inquiries.id = tags.inquiry_id WHERE users.id = ? GROUP BY inquiries.id;", session["user_id"])
    
    # might need to work on the commenting/accepting request feature first. 
    # need stuff to fill interactions table to track the lending and the borrowing.
    #for inquiry in myInquiries:
        
        
    return render_template("interactions.html")

