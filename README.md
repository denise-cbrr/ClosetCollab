Closet Collab

Video: https://youtu.be/yCJr8lWnNeI

Short Description
Welcome to Closet Collab! Closet Collab is a platform where students at Yale can borrow and lend each other clothes. Yale’s  countless events like club interviews, college formals, dance performances, and even frat parties, often leaves students with a need for various different types of clothing. Unfortunately, not all students are well acquainted with a variety of people, making it difficult for some to find the clothes they need. With Closet Collab, we hope to build a safe platform where students can easily inquire about the clothes they need and lend their clothes to other students in need. 

Installation
Before running our program, here are a few things one may need to install:
    Install the right Visual Studio Code for your computer’s software
      Via your terminal or extensions section in VS Code
        - Install a Python version higher than 3.6 (https://code.visualstudio.com/docs/python/python-tutorial)
        - Install SQLite3 (https://www.sqlite.org/download.html)
        - Install Jinja (you can find this in the extensions tab)
        - Install pip (https://pip.pypa.io/en/stable/installation/)
    
    Import the project into VS Code
      - Unzip the project file outside of VS Code
      - Import and open the project folder in VS Code   
    
    Setting up a virtual environment
      macOS and Linux
        - To install: python -m venv /path/to/new/virtual/environment
        - To run: source <venv>/bin/activate
      Windows
        - To install: python -m venv C:\path\to\new\virtual\environment
        - To run: C:\> <venv>\Scripts\activate.bat

Refer to the documentation for other questions: https://docs.python.org/3/library/venv.html

    Installing other libraries
      In a virtual environment within the project directory, run:
        - pip install -r requirements.txt

Website Walkthrough

About Us Page
When users first access our website, they are brought to our “About Us” page. This page features a short description of what ClosetCollab is about, explaining the website’s purpose and intentions. Here, users are presented with an interactive navigation bar filled with links that redirect the user to the different pages of our website. However, if the user is not logged in, each link, aside from “Register” and “Feed” will automatically direct them to the “Login” page.

Register Page
If users choose to register after visiting our “About Us” page, they are redirected to a form that allows them to create their account. They are prompted to put their name, email, username, password, password confirmation, and Yale residential college. Users are notified if: the username they’ve inputted already exists, the email address is not in a valid email format, and the password and password confirmation do not match. When users finally have all valid information and submit the form, they are then redirected to the “Login” page, where they log in to authenticate their accounts. 

Login Page
If the user was not logged in while they clicked through in the “About Us” page, they are redirected to the “Login” page. This page asks the users for their username and password. If the username does not exist, or the username and password does not match, the user is redirected to an apology page informing them of that error. If the username and password do match, the user is then redirected to the “Feed” page. 

Feed Page
In our “Feed” page, users can view and respond to ongoing inquiries, meaning the inquiries have not reached their expiration date nor have been resolved. The feed is populated by returning inquiries based on their post date. The most recent inquiries are the first ones to show up in the feed. Users do not have to be logged into a session in order to access the feed, they are able to view the feed through the “About Us” page, however, in order to add an inquiry or respond to others’ inquiries, they must be logged into their session. 

At the top of the “Feed” page, users can find an “Add Inquiry” button, where when clicked, the button reveals a pop up form. This form asks the users for a request description, item style(s), item size, item type (e.g. shirt, jacket, jeans), and the date that the article of clothing is needed by. When the user submits their inquiry, they inquiry is automatically returned to be visible in the “Feed” page. 

Item styles, size, and type are all tags that are a part of the inquiry form because we’ve implemented a filtering system allowing the users to filter through relevant inquiries. Users can choose to use one or more of the three filters to use, and when they apply the filters, the feed is repopulated to only show those with all of the tags chosen. This allows the user to easily find inquiries that they can respond to without having to scroll through an endless list of inquiries in their feed. 

Inquiry Page
Once the user finds the inquiry they would like to respond to, they can click the “Respond to Request” button that will direct them to a new page called “Inquiry.” If the user accessing the page is the original poster of the inquiry, they are able to see all responses to their inquiry, with each response displaying two buttons: “Accept” and “Decline”. When the user confirms the changes after clicking “Accept,” all inquiries except for the accepted one will be deleted from the page. All declined responses are also deleted when the user confirms the changes they’ve created. 

If the user accessing this page was not the original poster of the inquiry, they will also be able to see all other responses to that inquiry, along with a form to submit their response. In the response form they are asked for an item description, item picture, and a return date for when they want the item back. When users submit their response, the response is automatically rendered into the inquiry page and it will be the first one on the page. 

Interactions Page
With all of the borrowing and lending happening, it would be helpful for the user to be able to track all of their interactions, hence the “Interactions” page. The page is divided in half, with the right side displaying all of the user’s currently accepted inquiries so they could track the lender, item, and return date of the article of clothing that they borrowed. On the left side, all of the user’s lending interactions are displayed, showing the user the borrower, the item, and the return date they want it by. 

We’ve implemented a verification for both the borrower and the lender. After accepting, the borrower has a button on the inquiry asking if the item has been received. Once the borrower confirms this, the status of the inquiry changes to “in progress.” On the lender’s end now, a new button shows up by the inquiry asking if the item has been returned. When the lender confirms the return, the inquiry’s status will change to “completed.” If the borrower never received the item in the first place and the expiration date of the inquiry has passed, the inquiry status will change to “late.” And if the lender never confirms the item’s return, the inquiry status will change to “lost.”

Profile Page
The user has their own profile page where they can view their information and update their profile picture. This page also has all of their ongoing inquiries, meaning those that haven’t expired nor been satisfied. 

Logout
When the user is satisfied with their session, they can easily log out of their account by clicking the “Logout” button on the navigation bar. 
