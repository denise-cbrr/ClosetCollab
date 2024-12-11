import sqlite3
import os
import hashlib
from datetime import datetime
from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory, Response, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required

#Tables:
#users table
    #id: user's id (uniquely defines each)
    #username: unique and user created
    #password: password to user's login
    #college: (one of 14) Yale residential colleges
    #name: user's name
    #img_path: path to the image for the user's profile picture (Are we doing default ones??)

#inquiries table
    #id: inquiry_id
    #user_id: id of the poster
    #accepted: "yes" or  "no" (default is no)
    #time_published: YYYY-MM-DD HH:MI:SS
    #request: user's reason
    #exp_date: YYYY-MM-DD

#tags table
    #inquiry_id: references inquiries table (id)
    #tag: text (anything from style, size, type)

#interactions table
    #user_id: person who is doing the borrowing, also references users (id)
    #lender_id: person who is doing the lending, also references users (id)
    #inquiry_id: references inquiries (id)
    #status: text (pending, in progress, completed, lost, late)

#responses table 
    #id: identifies the responses
    #inquiry_id: references inquiries(id)
    #prosp_lender_id: references users(id), and is an identifier of who user could be borrowing from
    #time_published: to sort by time/date
    #reply: text

# Configure application
app = Flask(__name__)

# Folders where uploaded images will be stored
ROOT_PATH = os.path.dirname(__file__)
STATIC_DIR = os.path.join(ROOT_PATH, 'static')
PROFILE_UPLOAD = os.path.join(STATIC_DIR, 'profile')
RESPONSES_UPLOAD = os.path.join(STATIC_DIR, 'responses')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['PROFILE_UPLOAD'] = PROFILE_UPLOAD
app.config['RESPONSES_UPLOAD'] = RESPONSES_UPLOAD


# Ensure upload folder exists
os.makedirs(PROFILE_UPLOAD, exist_ok=True)
os.makedirs(RESPONSES_UPLOAD, exist_ok=True)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
Session

# Source: https://flask.palletsprojects.com/en/stable/tutorial/database/, consulted for information on how to handle sqlite3 and flask outside of CS50
# Retrieves database's connection (to perform SQL query searches)
def get_db():
    """Opens a new database connection if one doesn't exist"""
    if 'db' not in g:
        g.db = sqlite3.connect('closet.db')

        # Makes it so that dictionary-like rows, accessible by their column names, are returned
        g.db.row_factory = sqlite3.Row  
    return g.db

# Source: https://flask.palletsprojects.com/en/stable/tutorial/database/, consulted for information on how to handle sqlite3 and flask outside of CS50
# Function to close the database connection
# Automatically called by Flask when a request is completed
@app.teardown_appcontext
def close_db(exception):
    """Closes the database connection at the end of the request"""
    db = g.pop('db', None)

    # Checks whether a database connection was found; if so, closes it
    if db is not None:
        db.close()

def validate_date_field(field_var, field_name):
    """Validate that the date field is not empty, has a valid format, and exists in the future."""
    if not field_var:
        return apology(f"{field_name} is required.", 400)
    
    try:
        # Try parsing the date
        field_var_date = datetime.strptime(field_var, "%Y-%m-%d")
        
        # Ensure the date is in the future
        if field_var_date <= datetime.now():
            return apology(f"{field_name} must be in the future or today", 400)
        
    except ValueError:
        # Signal to the user that this is an invalid date type
        return apology(f"Invalid {field_name} format. Use YYYY-MM-DD.", 400)

    return None  # If everything is fine, return None


# Retrieves all information (available in the users table) about the user whose id is the parameter
def get_lender_info(user_id):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

# Checks if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Source: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/, consulted for information on uploading and displaying images        
# Function for image uploads to return an img_path to be inserted into respective SQL tables
def upload_image(img_name, folder_name):
    
    # Checks if there is an image uploaded
    if img_name not in request.files:
            return apology ("No image uploaded", 400)
        
    file = request.files[img_name]  
    
    # Double checks if there was a file selected
    if not file.filename:
        return apology("No selected file.", 400)
        
    # Checks if the file type is an allowed type     
    if not allowed_file(file.filename):
        return apology("File type not allowed.", 400)
    
    # Changes the filename into a safer version without any special characters 
    filename = secure_filename(file.filename)
    
    # From the os library, joins the folder name and file name into a path
    file_path = os.path.join(app.config[folder_name], filename)
    print(file_path)
    file.save(file_path)    # Saves the file to the path 
    
    # Returns the path to the image. Ex: "profile/img1.jpg"
    return os.path.relpath(file_path, STATIC_DIR)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Renders index.html, an about page where a user can also log in/register
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

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

        # fetchone fetches the first row of the results, aka the user whose username matches
        person = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        # Ensure username belongs to a valid user and password is correct
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

    # Redirect user to about page (index.html)
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = request.form.get("name")

        # Ensures name is not just spaces
        check_name = request.form.get('name', '').strip()
        if not check_name:
            return apology("You cannot have a name composed of just spaces.", 400)

        # Ensures username is not just spaces
        username = request.form.get("username")
        check_username = request.form.get('username', '').strip()
        if not check_username:
            return apology("You cannot have a username composed of just spaces.", 400)

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
    """Generates feed that user sees"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Processes form when user posts a new inquiry to feed
        userRequest = request.form.get("userRequest")

        # Ensures user isn't just submitting white space as a inquiry request
        check_request = request.form.get('userRequest', '').strip()
        if not check_request:
            return apology('Request cannot be empty or only spaces.', 400)

        # Creates a list from the style tags (the tags that the user selects to describe their inquiry)
        tags_list = request.form.getlist("style")   
        
        # Extends list to include size and item, puts "None" if item left blank
        tags_list.extend(filter(None, [request.form.get("size"), request.form.get("item")])) 

        expirationDate = request.form.get("expirationDate")
        curUser = session["user_id"]
        
        # Validating the backend, ensure what's required is reinforced
        if not userRequest:
            return apology("Request description is required.", 400)
        validation_error = validate_date_field(expirationDate, "Expiration Date")
        if validation_error:
            return validation_error
        if not request.form.get("size"):
            return apology("Please specify a size", 400)

        db = get_db()  
        # Updates inquiries table with the new inquiry
        db.execute(
            "INSERT INTO inquiries (request, exp_date, user_id) VALUES (?, ?, ?)",
            (userRequest, expirationDate, curUser)
        )
        
        # Returns the id of the newest inquiry
        inquiry_id = db.execute(
            "SELECT id FROM inquiries ORDER BY id DESC LIMIT 1"
        ).fetchone()[0] 

        # Updates tags table to include the tags of the newest inquiry with respect to its id
        for tag in tags_list:
            db.execute(
                "INSERT INTO tags (inquiry_id, tag) VALUES (?, ?)",
                (inquiry_id, tag)
            )
        db.commit()

        return redirect(url_for('feed'))
    else:
        # Implements filter system
        tags = request.args.getlist("styleFilter")
        size_filter = request.args.get("sizeFilter")
        type_filter = request.args.get("typeFilter")
        
        # Creates the filtered feed if at least one filter is used
        if tags or size_filter or type_filter:
            
            # If there is a size filter, add to the tags list
            if size_filter:
                tags.append(size_filter)
                
            # If there is a type filter, add to the tags list
            if type_filter:
                tags.append(type_filter)
                
            tag_count = len(tags)
            
            # Sources: https://www.peterspython.com/en/blog/show-the-values-in-sqlalchemy-dynamic-filters and ChatGPT
            # Consulted both sources to learn and implement dynamic filtering to accommodate for tags
            # Creates placeholders, e.g. ('?', '?', '?') where the number of '?' correspond to the number of tags
            
            placeholders = ', '.join(['?'] * len(tags))
        
            db = get_db()

            # Raw SQL query that will return information about every inquiry (and the user that posted them) given it includes the tags that were selected
            query = f"""
                SELECT users.name, users.username, users.college, users.img_path, inquiries.*, 
                GROUP_CONCAT(tags.tag, ', ') AS tags FROM inquiries 
                JOIN users ON users.id = inquiries.user_id 
                JOIN tags ON inquiries.id = tags.inquiry_id 
                WHERE tags.tag IN ({placeholders})
                AND inquiries.accepted = 'no'
                AND inquiries.exp_date >= CURRENT_DATE 
                GROUP BY inquiries.id HAVING COUNT(tags.tag) = ? 
                ORDER BY inquiries.time_published DESC;"""
        
            # Source: https://medium.com/@ajay.monga73/sql-injection-prevention-for-c-developers-parameterized-queries-explained-b5a4cb1b6207
            # Consulted source about parametrized queries and protecting from SQL injection attacks
            # Put parameters into the above query: tags will be placed into the placeholders and tag_count is used to specify the number of matching 
            results = db.execute(query, tags + [tag_count]).fetchall()
            return render_template("feed.html", results=results)
        
        # Renders an unfiltered feed when no filters are used
        db = get_db()

        # Returns information about all inquiries (including all their tags, user details) where the inquiries have not expired and have not been accepted yet
        results = db.execute("""
            SELECT users.name, users.username, users.college, users.img_path, inquiries.*, 
            GROUP_CONCAT(tags.tag, ', ') AS tags FROM users 
            JOIN inquiries ON users.id = inquiries.user_id 
            JOIN tags ON inquiries.id = tags.inquiry_id
            WHERE inquiries.exp_date >= CURRENT_DATE 
            AND inquiries.accepted = 'no'
            GROUP BY inquiries.id 
            ORDER BY inquiries.time_published DESC;""").fetchall()
        
    # Delete any inquiries that the user hasn't accepted any responses in, and the expiration date has passed (affects other tables like tags and responses as well)
        db.execute("DELETE FROM inquiries WHERE accepted ='no' AND exp_date < CURRENT_DATE")
        db.execute("DELETE FROM tags WHERE inquiry_id NOT IN (SELECT id FROM inquiries)")
        db.execute("DELETE FROM responses WHERE inquiry_id NOT IN (SELECT id FROM inquiries)")

    return render_template("feed.html", results=results)

@app.route("/inquiry/<int:inquiry_id>", methods=["GET", "POST"])
@login_required
def inquiry(inquiry_id):
    """Generates a page for each inquiry to see its individual responses/selections"""

    db = get_db()
    # Determine which inquiry user is viewing
    inquiry = db.execute("""
       SELECT * FROM inquiries
        WHERE id = ?
    """, (inquiry_id,)).fetchone()

    # Checks if user is viewing their own post 
    curUser = session["user_id"]
    is_owner = inquiry["user_id"] == curUser
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # When a response form is submitted
        if "replyResponse" in request.form:
            reply = request.form.get("replyResponse")
            check_reply = request.form.get('replyResponse', '').strip()
            curUser = session["user_id"]
            lending_exp_date = request.form.get("lending_exp_date")

            # Ensure that user isn't submitting just white space into reply
            if not check_reply:
                return apology('Request cannot be empty or only spaces.', 400)

            # Validate backend
            if not reply:
                return apology("Response description is required.", 400)
            
            # Ensure that lending_exp_date is in the future
            validation_error = validate_date_field(lending_exp_date, "Return Date")
            if validation_error:
                return validation_error

            # Calls on the function to return a path to the item image
            # Path will be inserted into responses table
            file_path = upload_image("replyPic", "RESPONSES_UPLOAD")
            
            # Inserts new response into response table
            db.execute(
                "INSERT INTO responses (inquiry_id, prosp_Lender_id, reply, img_path, lending_exp_date) VALUES (?, ?, ?, ?, ?)",
                (inquiry_id, curUser, reply, file_path, lending_exp_date)
            )

        # User reached route by clicking on the confirm button (to confirm what they're deleting or accepting)
        else:
            # Check for the existence of an accepted_id, a response to the inquiry the user posted that they've now also accepted
            accepted_id = request.form.get("accepted_id")
            if accepted_id:
                # Identify the lender via lenderId, or who posted that response
                lenderId = db.execute("SELECT prosp_Lender_id FROM responses WHERE id = ?", (accepted_id, )).fetchone()[0]

                # Add this relationship to the interactions table 
                update = db.execute("INSERT INTO interactions (inquiry_id, status, lender_id, user_id) VALUES (?, ?, ?, ?)", 
                (inquiry_id, "pending", lenderId, curUser))
                
                # Identify lender from their lenderId for future contact reference
                lender_info = get_lender_info(lenderId)

                # Delete all other responses to this inquiry that are not the one that had been accepted
                db.execute("DELETE FROM responses WHERE inquiry_id = ? AND id != ?", (inquiry_id, accepted_id))

                # Update in inquiries that this specific inquiry has been accepted
                db.execute("UPDATE inquiries SET accepted = 'yes' WHERE id = ?", (inquiry_id, ))
                db.commit()
            else:
                # Deletes the responses that the user had declined for this inquiry
                declined_ids = request.form.get("declined_ids").split(',')
            
                for id in declined_ids:
                    db.execute("DELETE FROM responses WHERE id = ?", (id, ))
    
    # Delete any responses whose return dates precede the current date
    db.execute("DELETE FROM responses WHERE lending_exp_date < CURRENT_DATE")

    # Retrieve information regarding the responses to the id of the inquiry the user is currently interacting with
    responses = db.execute(
        "SELECT responses.*, users.name, users.username, users.college, users.img_path AS profile FROM responses JOIN users ON responses.prosp_Lender_id = users.id WHERE responses.inquiry_id = ? ORDER BY responses.time_published DESC", (inquiry_id, )).fetchall();

    # Identify whether or not the inquiry has been accepted
    inquiry_accepted = db.execute("SELECT accepted FROM inquiries WHERE id = ?", (inquiry_id, )).fetchone()[0]
    db.commit()

    # Inquiry has been accepted: render accepted_inquiry.html and display lender's contact info
    # This also prevents users from pressing the back arrow and resubmitting another (potentially) different response, and adding that to our database as well
    if inquiry_accepted == 'yes':
        lenderId = db.execute("SELECT lender_id FROM interactions WHERE inquiry_id = ?", (inquiry_id, )).fetchone()[0]
        lender_info = get_lender_info(lenderId)
        return render_template("accepted_inquiry.html", lender_info=lender_info)
    # Display regular responses
    else:
        return render_template("inquiry.html", responses=responses, inquiry=inquiry, is_owner=is_owner)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Display user's profile"""
    curUser = session["user_id"]
    db = get_db()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Deals with photos
        file_path = upload_image("profilePic", "PROFILE_UPLOAD")        
        # Updates user profile picture    
        db.execute("UPDATE users SET img_path = ? WHERE id = ?", (file_path, session["user_id"]))

    # Retrieves the information for the inquiries posted by the current user, newest first
    inquiries = db.execute(
        "SELECT * FROM inquiries WHERE user_id = ? ORDER BY exp_date DESC", (curUser, )).fetchall();
    
    # Retrieves information about the current user
    user = db.execute(
        "SELECT name, username, college FROM users WHERE id = ?", (curUser, )).fetchone();
    
    # Retrieves the picture the user has set as their profile picture
    pic = db.execute("SELECT img_path FROM users WHERE id = ?", (curUser, )).fetchone();
    
    if pic:
        img_path = pic[0]  # Access the first column (img_path)

    db.commit()
    return render_template("profile.html", inquiries=inquiries, user=user, picture=img_path)

@app.route("/interactions", methods=["GET", "POST"])
@login_required
def interactions():
    """Displays user's lending and borrowing interactions"""
    db = get_db()
    curUser = session["user_id"]
    
    # Marks status as late for interactions where the status is still pending (aka lender hasn't successfully delivered their clothing item
    # to the user) by the time the inquiry's expiration date has passed
    db.execute(
        """
        UPDATE interactions
        SET status = 'late'
        WHERE status = 'pending'
        AND inquiry_id IN (
            SELECT id
            FROM inquiries
            WHERE exp_date < DATE('now')
        )
        """
    )

    # Marks status as lost for interactions where the status is still in progress (aka user hasn't successfully returned their clothing item
    # to the lender) by the time that item's lending return date has passed
    db.execute(
        """
        UPDATE interactions
        SET status = 'lost'
        WHERE status = 'in progress'
        AND inquiry_id IN (
            SELECT id
            FROM responses
            WHERE lending_exp_date < DATE('now')
        )
        """
    )

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # user has received the clothing they are borrowing 
        if "receiveButton" in request.form:
            inquiry_id = request.form["inquiry_id"]
            db.execute("UPDATE interactions SET status = 'in progress' WHERE inquiry_id = ?", (inquiry_id, ))
        
        # user has returned the clothing they are borrowing 
        if "returnButton" in request.form:
            inquiry_id = request.form["inquiry_id"]
            db.execute("UPDATE interactions SET status = 'completed' WHERE inquiry_id = ?", (inquiry_id, ))

        # if user selects delete, this interaction gets deleted, and so does the inquiry_id of it get removed from inquiries, 
        # responses, and tags as well
        if "inquiry_id_delete" in request.form:
            inquiry_id_delete = request.form.get("inquiry_id_delete")
            db.execute("DELETE FROM inquiries WHERE id = ?", (inquiry_id_delete, ))
            db.execute("DELETE FROM tags WHERE inquiry_id = ?", (inquiry_id_delete, ))
            db.execute("DELETE FROM responses WHERE inquiry_id = ?", (inquiry_id_delete, ))
            db.execute("DELETE FROM interactions WHERE inquiry_id = ?", (inquiry_id_delete, ))

    # Retrieve all interactions where the current user is borrowing an item from someone else            
    borrow_interactions = db.execute(
    """
        SELECT
            inquiries.request, inquiries.exp_date, interactions.*, 
            responses.lending_exp_date, responses.img_path AS item_img, 
            users.name, users.username, users.img_path AS user_img, users.college
            FROM inquiries 
            JOIN interactions ON inquiries.id = interactions.inquiry_id
            JOIN responses ON inquiries.id = responses.inquiry_id
            JOIN users ON interactions.lender_id = users.id
            WHERE interactions.user_id = ?
    """,(curUser, )).fetchall()
    
    # Retrieve all interactions where the current user is lending an item to someone else    
    lender_interactions = db.execute(
        """SELECT
            inquiries.request, inquiries.exp_date, interactions.*, 
            responses.img_path, responses.lending_exp_date,
            users.name, users.username, users.img_path AS user_img, users.college
            FROM inquiries 
            JOIN interactions ON inquiries.id = interactions.inquiry_id
            JOIN responses ON inquiries.id = responses.inquiry_id
            JOIN users ON interactions.user_id = users.id
            WHERE interactions.lender_id = ?
    """,(curUser, )).fetchall()

    db.commit()
    return render_template("interactions.html", borrow_interactions=borrow_interactions, lender_interactions=lender_interactions)

