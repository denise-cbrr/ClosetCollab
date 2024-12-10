import sqlite3
import os
import hashlib
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, Response, g
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
    #inquiry_id
    #tags: anything from style to size

#interactions
    #user_id
    #inquiry_id
    #status: text (delivered, received, etc.)
    #lender_id: user_id of lender

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

# Consulted: https://flask.palletsprojects.com/en/stable/tutorial/database/, for information on how to handle sqlite3 and flask outside of CS50
# Retrieves database's connection (to perform SQL query searches)
def get_db():
    """Opens a new database connection if one doesn't exist"""
    if 'db' not in g:
        g.db = sqlite3.connect('closet.db')

        # Makes it so that dictionary-like rows, accessible by their column names, are returned
        g.db.row_factory = sqlite3.Row  
    return g.db

# Consulted: https://flask.palletsprojects.com/en/stable/tutorial/database/, for information on how to handle sqlite3 and flask outside of CS50
# Function to close the database connection
# Automatically called by Flask when a request is completed
@app.teardown_appcontext
def close_db(exception):
    """Closes the database connection at the end of the request"""
    db = g.pop('db', None)

    # Checks whether a database connection was found; if so, closes it
    if db is not None:
        db.close()

# Retrieves all information (available in the users table) about the user whose id is the parameter
def get_lender_info(user_id):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

# Checks if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
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
    
    #
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
    """Generates feed that user sees"""
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        userRequest = request.form.get("userRequest")

        # Creates a list from the style tags (the tags that the user selects to describe their inquiry)
        tags_list = request.form.getlist("style")   
        
        # Extends list to include size and item, puts "None" if item left blank
        tags_list.extend(filter(None, [request.form.get("size"), request.form.get("item")]))    
        expirationDate = request.form.get("expirationDate")
        curUser = session["user_id"]
        
        db = get_db()  
        # Updates inquiries table with a new inquiry
        db.execute(
            "INSERT INTO inquiries (request, exp_date, user_id) VALUES (?, ?, ?)",
            (userRequest, expirationDate, curUser)
        )
        
        # Returns the id of the newest inquiry
        inquiry_id = db.execute(
            "SELECT id FROM inquiries ORDER BY id DESC LIMIT 1"
        ).fetchone()[0] 

        # Updates tags table to include the tags of the newest inquiry
        for tag in tags_list:
            db.execute(
                "INSERT INTO tags (inquiry_id, tag) VALUES (?, ?)",
                (inquiry_id, tag)
            )
        db.commit()
        
        # Returns information of every inquiry that is not expired or accepted
        results = db.execute("""SELECT users.name, users.username, users.college, users.img_path, inquiries.*, 
                             GROUP_CONCAT(tags.tag, ', ') AS tags FROM users 
                             JOIN inquiries ON users.id = inquiries.user_id 
                             JOIN tags ON inquiries.id = tags.inquiry_id
                             WHERE inquiries.exp_date >= CURRENT_DATE 
                             AND inquiries.accepted = 'no'
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
                SELECT users.name, users.username, users.college, users.img_path, inquiries.*, 
                GROUP_CONCAT(tags.tag, ', ') AS tags FROM inquiries 
                JOIN users ON users.id = inquiries.user_id 
                JOIN tags ON inquiries.id = tags.inquiry_id 
                WHERE tags.tag IN ({placeholders})
                AND inquiries.accepted = 'no'
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
            results = db.execute("""SELECT users.name, users.username, users.college, users.img_path, inquiries.*, 
                                 GROUP_CONCAT(tags.tag, ', ') AS tags FROM users 
                                 JOIN inquiries ON users.id = inquiries.user_id 
                                 JOIN tags ON inquiries.id = tags.inquiry_id
                                 WHERE inquiries.exp_date >= CURRENT_DATE 
                                 AND inquiries.accepted = 'no'
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

    #Checks if user is viewing their own post 
    curUser = session["user_id"]
    is_owner = inquiry["user_id"] == curUser
    
    if request.method == "POST":
        if "replyResponse" in request.form:
            reply = request.form.get("replyResponse")
            curUser = session["user_id"]
            lending_exp_date = request.form.get("lending_exp_date")

            # Calls on the function to return a path to the item image
            # Path will be inserted into responses table
            file_path = upload_image("replyPic", "RESPONSES_UPLOAD")
            
            db.execute(
                "INSERT INTO responses (inquiry_id, prosp_Lender_id, reply, img_path, lending_exp_date) VALUES (?, ?, ?, ?, ?)",
                (inquiry_id, curUser, reply, file_path, lending_exp_date)
            )
        else:
            accepted_id = request.form.get("accepted_id")
            if accepted_id:
                # LOL i have so many print statements cuz the things kept on breaking
                # I avoided joining interactions with inquiries, so for now, there is a slight duplication of having user_id be in interactions too
                lenderId = db.execute("SELECT prosp_Lender_id FROM responses WHERE id = ?", (accepted_id, )).fetchone()[0]
                # """SELECT responses.prosp_Lender_id, users.img_path FROM responses JOIN users ON responses.prosp_Lender_id = users.id WHERE responses.id = ?""", (accepted_id, )
                update = db.execute("INSERT INTO interactions (inquiry_id, status, lender_id, user_id) VALUES (?, ?, ?, ?)", 
                (inquiry_id, "pending", lenderId, curUser))

                lender_info = get_lender_info(lenderId)

                # Get all other responses in that inquiries that will need to be deleted from the database
                to_be_deleted = db.execute("SELECT * FROM responses WHERE inquiry_id = ? AND id != ?", (inquiry_id, accepted_id)).fetchall()
                if to_be_deleted:
                    for row in to_be_deleted:
                        db.execute("DELETE FROM responses WHERE id = ?", (row['id'], ))

                db.execute("UPDATE inquiries SET accepted = 'yes' WHERE id = ?", (inquiry_id, ))
                print(f"Updating inquiry with id {inquiry_id} to accepted = 'yes'")
                db.commit()

                return render_template("accepted_inquiry.html", lender_info=lender_info)
            else:
                # Deletes the responses that the user declines
                declined_ids = request.form.get("declined_ids").split(',')
            
                for id in declined_ids:
                    db.execute("DELETE FROM responses WHERE id = ?", (id, ))
    
    db.execute("DELETE FROM responses WHERE lending_exp_date < CURRENT_DATE")

    db.execute("DELETE FROM inquiries WHERE accepted ='no' AND exp_date < CURRENT_DATE")
    db.execute("DELETE FROM tags WHERE inquiry_id NOT IN (SELECT id FROM inquiries)")
    db.execute("DELETE FROM responses WHERE inquiry_id NOT IN (SELECT id FROM inquiries)")

    responses = db.execute(
        "SELECT responses.*, users.username AS lender_username FROM responses JOIN users ON responses.prosp_Lender_id = users.id WHERE responses.inquiry_id = ? ORDER BY responses.time_published DESC", (inquiry_id, )).fetchall();
        #"SELECT * FROM responses WHERE inquiry_id = ? ORDER BY time_published DESC", (inquiry_id,)
        #).fetchall()
        
        #another to-do = check all the expiration dates 
        # if user clicks an accept, the rest automatically deletes and needs to be removed from SQL query
        # if user clicks accept, add to interactions table and 
        # change the status in the original feed table
        # return user to a new html page "Please refer to interactions table, here's other user's email"
        # for declines, delete all SQL queries FROM replies (they are an array of ids)
    
    #pics = [row['img_path'] for row in db.execute("SELECT img_path FROM responses WHERE inquiry_id = ?", (inquiry_id,)).fetchall()]
    #print(pics)
    for response in responses:
        print(response['img_path'])
    
    
        
    inquiry_accepted = db.execute("SELECT accepted FROM inquiries WHERE id = ?", (inquiry_id, )).fetchone()[0]
    db.commit()
    if inquiry_accepted == 'yes':
        lenderId = db.execute("SELECT lender_id FROM interactions WHERE inquiry_id = ?", (inquiry_id, )).fetchone()[0]
        lender_info = get_lender_info(lenderId)
        return render_template("accepted_inquiry.html", lender_info=lender_info)
    else:
        return render_template("inquiry.html", responses=responses, inquiry=inquiry, is_owner=is_owner)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    if request.method == "POST":
        #Deals with photos
        file_path = upload_image("profilePic", "PROFILE_UPLOAD")            
        db.execute("UPDATE users SET img_path = ? WHERE id = ?", (file_path, session["user_id"]))
        #return redirect(url_for('download_file', name=filename))
            
    db = get_db()
    curUser = session["user_id"]
    inquiries = db.execute(
        "SELECT * FROM inquiries WHERE user_id = ? ORDER BY exp_date DESC", (curUser, )).fetchall();
    
    user = db.execute(
        "SELECT name, username, college FROM users WHERE id = ?", (curUser, )).fetchone();
    
    pic = db.execute("SELECT img_path FROM users WHERE id = ?", (curUser, )).fetchone();
    #cursor.execute("SELECT img_path, file_type FROM users WHERE id = ?", (curUser, ))
    
    if pic:
        img_path = pic[0]  # Access the first column (img_path)
    
    print(img_path)
    
    #row = cursor.fetchone()
    #if row:
        #imgdata = row[0]
        #file_extension = row[1]
    
    #if imgdata:
        #with open(f'retrieved_image{file_extension}', 'wb') as f:
            #picture_path = f.write(imgdata)
    #else:
        #picture_path = None
    
    #print(f"path: {picture_path}")
    db.commit()
    return render_template("profile.html", inquiries=inquiries, user=user, picture=img_path)
    #picture = url_for('return_image', table="users", id=curUser) 
    #print(f"picture url: {picture}")
            
    #return render_template("profile.html", inquiries=inquiries, user=user, picture=picture)



@app.route('/profile/<name>')
def download_file(name):
    return send_from_directory(app.config["PROFILE_UPLOAD"], name)

@app.route('/responses/<name>')
def uploaded_file(name):
    return send_from_directory('responses', name)

#@app.route('/return_image/<string:table>/<int:id>')
#def return_image(table, id):
    #valid_tables = {"users", "responses"}
    
    #if table not in valid_tables:
        #return apology ("can't find table", 400)
     
    #query = f"SELECT img_data, file_type FROM {table} WHERE id = ?"
    
    #db = get_db()
    #cursor = db.cursor()
    #cursor.execute(query, (id,)).fetchone()
    
    #row = cursor.fetchone()
    #if not row:
       #return apology("no image found")
    
    #imgbin = row[0]
    #file_extension = row[1]
    
    #mime_type = f"image/{file_extension.strip('.')}"
        
    #return Response(imgbin, mimetype=mime_type)
    


@app.route("/interactions", methods=["GET", "POST"])
@login_required
def interactions():
    db = get_db()
    curUser = session["user_id"]
    
     # person didn't receive it in time: aka LATE
    db.execute(
        """
        UPDATE interactions
        SET status = 'late'
        WHERE status = 'pending'
        AND inquiry_id IN (
            SELECT id
            FROM inquiries
            WHERE exp_date < DATE('now', '+5 day')
        )
        """
    )

    db.execute(
        """
        UPDATE interactions
        SET status = 'lost'
        WHERE status = 'in progress'
        AND inquiry_id IN (
            SELECT id
            FROM responses
            WHERE lending_exp_date < DATE('now', '+5 day')
        )
        """
    )

    # if lender doesn't get their item back 
    # for interaction in lender_interactions:
        
    
    if request.method == "POST":
        # go through all the interactions, and if status = pending but the expiration date has past, then status should be late?
        # Check if accepted button was pressed
        if "receiveButton" in request.form:
            inquiry_id = request.form["inquiry_id"]
            db.execute("UPDATE interactions SET status = 'in progress' WHERE inquiry_id = ?", (inquiry_id, ))
                
        if "returnButton" in request.form:
            inquiry_id = request.form["inquiry_id"]
            db.execute("UPDATE interactions SET status = 'completed' WHERE inquiry_id = ?", (inquiry_id, ))

        if "inquiry_id_delete" in request.form:
            inquiry_id_delete = request.form.get("inquiry_id_delete")
            db.execute("DELETE FROM inquiries WHERE id = ?", (inquiry_id_delete, ))
            db.execute("DELETE FROM tags WHERE inquiry_id = ?", (inquiry_id_delete, ))
            db.execute("DELETE FROM responses WHERE inquiry_id = ?", (inquiry_id_delete, ))
            db.execute("DELETE FROM interactions WHERE inquiry_id = ?", (inquiry_id_delete, ))
                
    borrow_interactions = db.execute(
    """
        SELECT
            inquiries.request AS request, inquiries.exp_date AS exp_date, interactions.*, responses.lending_exp_date AS lending_exp_date, responses.img_path AS img_path
            FROM inquiries 
            JOIN interactions ON inquiries.id = interactions.inquiry_id
            JOIN responses ON inquiries.id = responses.inquiry_id
            WHERE interactions.user_id = ?
    """,(curUser, )).fetchall()
    # SELECT inquiries.request, interactions.*, responses.lending_exp_date FROM inquiries JOIN interactions ON inquiries.id = interactions.inquiry_id JOIN responses ON inquiries.id = responses.inquiry_id WHERE interactions.user_id = ?
    
    lender_interactions = db.execute(
        """SELECT
            inquiries.request AS request, responses.img_path AS img_path, interactions.*, responses.lending_exp_date AS lending_exp_date
            FROM inquiries 
            JOIN interactions ON inquiries.id = interactions.inquiry_id
            JOIN responses ON inquiries.id = responses.inquiry_id
            WHERE interactions.lender_id = ?
    """,(curUser, )).fetchall()

    for interaction in borrow_interactions:
        print(interaction['img_path'])
    
    # this would work for the borrowing side (maybe we can return less information compared to feed?)
    # myInquiries = db.execute("SELECT users.name, users.username, users.college, inquiries.*, GROUP_CONCAT(tags.tag) AS tags FROM users JOIN inquiries ON users.id = inquiries.user_id JOIN tags ON inquiries.id = tags.inquiry_id WHERE users.id = ? GROUP BY inquiries.id;", session["user_id"])
    
    # might need to work on the commenting/accepting request feature first. 
    # need stuff to fill interactions table to track the lending and the borrowing.
    #for inquiry in myInquiries:
    
    db.commit()
    return render_template("interactions.html", borrow_interactions=borrow_interactions, lender_interactions=lender_interactions)

