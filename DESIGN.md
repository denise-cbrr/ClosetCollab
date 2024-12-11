Closet Collab

Closet Collab uses a combination of Flask, Python, SQL, HTML, Javascript, and CSS. We’ve created multiple tables in our database, and implemented different routes connected to different pages. 

Tables we reference:
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

Backend:
Our backend implementation consists of Flask, Python, and SQL, and is primarily of different routes that return information to their respective HTML pages. 

Index Route (/):
When the user first enters our website, they are immediately directed to our “About Us” page via our index route. We included a navigation bar in all of our pages and from this users can already access a feed page, however they cannot submit any forms without logging in. 

Login Route (/login):
When the user accesses the “Login” page, they are automatically logged out of their session in order for them to log in. This route is full of validations using “if-else” statements and “try-except” statements that ensures the user is providing the correct information. The route checks that the user provides a valid username with valid characters, the user provides a password, and the user’s username and password are in the users database. To check the password, we used Werkzeug Security’s check_password_hash function in order to compare the password stored in the database to the password that the user entered. If any of the information provided is invalid, the users are shown an apology page  If the user logs in successfully, they are redirected to our “Feed” page, but if they fail to log in, they are redirected to the “Login” page again. The “Login” route is essential in ensuring that the user gets their own personalized pages such as: Feed, Profile, and Interactions. It is also essential in allowing users to post their own inquiries and responses. 

Log Out Route (/logout):
When the user clicks the Logout link, the route clears their session and forgets the user’s id, which logs them out. 

Register Route (/register):
In order to create their accounts, we’ve implemented a register route. Users will input their information into the form, which is then first validated by the route. We validate that the user has provided a name and username with valid characters, a valid email, and their residential college. We confirm that the user enters their password again to ensure that the passwords are correct and also confirm through an SQL query that their username does not already exist in our database. If there are no errors and apologies returned, the user’s information is then inserted into the users table using an SQL query.

Feed Route (/feed):
When the user logs in, they are redirected to feed.html and can view all ongoing inquiries. This HTML page is based off of the information populated by the information returned in “/feed.” This route uses both methods of “GET” and “POST” because it is accessible through a link and through submitting a form. 

When the webpage is accessed by “POST”, this means that the user submitted an inquiry to be displayed. We created a pop up form in the HTML page using a Bootstrap modal. The inquiry  form requires the user for a request description, item size, and a “need by” date, but it also gives them the option to add more tags such as item style (which users can select multiple) and item type. This information is passed into the route via the request.form.get function. Like login and register, we also validate the information that users provide, ensuring that the user provides all required fields on the form. 

When validations are done, the route prepares the information that will be inserted into the inquiries and tags table. We declare variables to hold the values of the request description, expiration date, and user id, which are then used in a tuple to insert a new inquiry into our inquiries table. Before inserting the inquiry into the tags table, we had to format all of the tags properly in order to iterate through them. We created a list that holds all style tags since the user can select more than one, or even none. The list is then extended to include the size tag and the item type tag, using “filter(None, ?)” to replace any null values with “None.” We then called an inquiry to select the id of the newest inquiry, holding that value in a variable. Since each tag is a row in the tags table, we iterate through the list using a for loop, and insert a new entry into the tags table using the inquiry id and the current tag in the iteration. When all of the insertions are done, the database commits the changes and the user is redirected to feed again. 

If the user accessed the feed using “GET” they can view all ongoing inquiries, meaning the inquiry has not expired and the poster has not accepted any responses yet. The inquiries can either be filtered or unfiltered depending on what the user decides. An unfiltered feed returns HTML cards showing the inquirer’s name, username, and residential college, along with the request description, tags, deadline date, and a “respond” button that will redirect the user to our response page. In order to return all of this information, we called a query in our route joining the users, inquiries, and tags table in order to select all inquiries that have not been accepted or expired. 

For a filtered feed, we show three dropdowns where the user can implement our preset filters of style, size, and type. When the user applies the filters, they are re-rendered a feed that returns only the ongoing inquiries that match all tags used in the filters. In order to select the right inquiries to be displayed, we had to accommodate for the tags table and create a dynamic SQL query. We first assign each filter type to a variable, with the style tags being a list. Then we check if at least one filter exists in order to create a dynamic SQL query. If the size and/or type filters were used, the tags list with the style filters are appended to include size and/or type. We then create a placeholders value in order to create the right amount of question marks for our dynamic query. We multiply the number of question marks by the length of the tags list. We also put the query in as variable in order to later protect ourselves from SQL injection attacks. When the query is ran, it returns all ongoing inquiries that include all of the tags in the filters. 

Regardless of whether this route is accessed via GET or POST, we will update our inquiries table by deleting any inquiries that the user hasn’t accepted a response in (aka there is no ongoing interaction between the poster of that inquiry and some lender) AND the expiration date (the date the user needed the item by) has passed. In other words, the user seemingly doesn’t need the item they are inquiring to borrow given they have not acted upon it and the date they needed said item by has passed. After deleting the inquiry, we must also delete any tags associated with it that were stored in our database, and we must delete any responses left for this inquiry. This way, we are clearing up space in our database, and the inquiries shown in the feed are current and realistic. 
 
Function: upload_image(img_name, folder_name)
The upload image function uses the Python library “os”, where the name of the file and the folder it will be stored in are passed down as arguments. 

The function validates that an image was uploaded, a file was selected, and if the file is an allowed file type (png, jpg, jpeg, gif). It will then take the filename and use the Werkzeug.utils function “secure_filename” to remove any non-safe characters from the name. This name will then be joined with the folder_name in order to create a file_path that leads to the picture’s location in the directory. The file path is saved into the server and then the function returns a path to the image relative to the static folder, allowing us to use flask’s “url_for()” function in our html templates. 

We created a function for saving and validating images to reduce redundancy in our inquiry and profile routes. 

Inquiry Route (/inquiry) & Inquiry.html:
When a user clicks on an inquiry in the feed (i..e clicking on the button labeled “Respond to Request”), they will access the inquiry route via GET and also take the id of said inquiry in as a parameter. What the user is able to see will be determined by whether or not they are accessing the page of one of their own inquiries or viewing an inquiry of someone else’s. We decided to do this to prevent a user from leaving replies to their own inquiries, and to ensure that only when a user is viewing their own inquiry can they “accept” or “decline” other users’ responses. The variable is_owner stores whether or not the user_id associated with the inquiry_id passed into the route (as a parameter) is the same as the user_id of the current session, and will be used later on as the primary condition (checking if it's true or false) to specify what the user can see on the page. Regardless of user_id’s value, a user will be able to see the inquiry’s request (aka, what the inquirer is requesting), and the deadline the inquirer will need said item by.

In inquiry.html, it is specified that only when is_owner is false (aka, the user is not viewing the page of an inquiry that they posted) can they post a response to the inquiry. The button will trigger a form to pop up, enforcing that the user must describe the item they are lending, provide a picture file of said item, and select which day they need the item returned to them by. For user convenience, they can press close to exit the pop up, or press submit to add their response; on submit, their inputs will be sent to the route for /inquiry via POST, and the user will be able to see their response displayed on this inquiry page. 

In the backend, we ensure that this submission is valid and reduce redundancy by only checking when the route is accessed through POST. Then, to handle this specific POST request (which is different from others), we first check if “replyResponse” is being submitted, because replyResponse is the required description users must put when completing a response. Similar to prior, we validate and retrieve the information submitted; this includes, ensuring that the date the user puts (the day they need the item back by) is not in the past (refers to another function, validate_date_field(), which compares current date with the expiration date, to do so), there are valid characters entered for the submitted response, and picture validation is handled in the upload_image function. We then update our responses table to include this new entry.

Our route also takes into consideration if a user is confirming their acceptance of a reply (aka indicating that they will borrow what that reply and its lender is offering) and/or their rejection (they don’t want what that response/lender is offering). Specified in our inquiry.html, all three buttons, the accept and decline buttons (attached to each reply for the inquiry), and the confirm button (used to send the ids of the responses the user intends to accept and/or delete) are only visible when a user is viewing the page of an inquiry they posted. 

Also in our html is javascript code that tracks the ids of the responses.Thus, on confirm (when user presses this button to confirm their choices), inquiry.html understands what changes to make to our database. The general logic following the javascript is that when the url for our inquiry page is first loaded, the id for what’s accepted is null, and the set for what’s to be deleted is empty. We chose to use set because we can directly remove and add elements just by referencing their id value (which is stored in our responses table), without the need to keep track of their indices; plus, as a user can delete multiple responses at once, and we can keep track of multiple ids this way. When the accept button is clicked, we remove any potential coloring for the decline button linked to that reply (aka red) and we remove this id from the to_be_deleted set (in the case that the user pressed decline earlier). We also check if there was a different previously accepted reply and change that reply back to its default (aka, no green coloring indicative of being selected) and our current reply id takes its place in variable acceptedReplyId (and also has a green “accept” button now for visual means). In order for the user to clear these buttons (aka they want a blank slate), they can refresh the page— which will re-trigger the javascript, setting the accepted id back to null, and the set containing what’s to be deleted as empty. 

The code for clicking the “decline” button on a response is very similar; that response’s id gets added to our to_be_deleted set, and if this response had been previously “accepted”, we remove any green coloring and set acceptedReplyId back to null. Our effort in being specific here was to ensure that a user can easily interact with these responses, change their mind on accepting some item vs. another, delete etc., and finally, only when the user presses confirm, do these selections have any permanent consequence. 

We also prohibit the user from pressing confirm without accepting or declining something (hence checking if the to_be_deleted set is still empty and there’s no accepted id). 

Via POST, our route will receive an array of response ids (our set was converted into an array to accommodate what data types a route can handle) that must be deleted from our response database,  or/and a response id that has been accepted. To reduce redundancy, we first check if accepted_id has a value; the logic behind is that if a response has been accepted, we have no need for any of the other responses linked to this inquiry, and thus we will remove all other responses regardless of whether or not all of them were present in the to_be_deleted array. 

Following if there was a response that was selected, we will add a new interaction to our interactions database, where the lender associated with the accepted response (aka whoever posted it), has a relationship with whoever posted the initial inquiry; their interaction status is set to “pending” which indicates that the lender has not yet successfully delivered the item to the poster, and we also update the inquiries database to denote that this inquiry has been accepted (aka it has been put into motion and the user is not still waiting for a reply that fits their request) by changing “accepted” from no to yes. As stated before, this means that the inquiry will no longer be visible on the home page as well, because the poster of that inquiry is no longer for potential lenders (they found one!). Reiterating what was said earlier, we will also remove all other responses to this inquiry that aren’t the one that had been accepted. 

If the user only declined responses and didn’t accept any— in other words, they only have a to_be_deleted set—then we iterate through the ids in that array, and delete those responses (with that corresponding id) from our responses database. Those responses will not be visible in the future either, due to this deletion. 

Regardless of whether /inquiry is accessed via GET or POST, we will remove any responses that are outdated in the sense that the return dates assigned to those precede the current date. We decided to do this because it doesn’t make sense for instance, for person A on Sunday the 20th to be able to make a decision (regarding to accept or decline) on person B’s prom dress if person B’s prom dress needed to be returned to them by Saturday the 9th. 

We use a query to identify whether or not the inquiry has been accepted; if accepted, we will render the accepted_inquiry page which displays that inquiry’s lender’s contact information. Because this is a condition, even if the user attempted to press the back arrow and re-submit the form, or if the user accessed this page through profiles, they will see that contact information even via GET. And if we had just accepted a reply, clicking confirm will return us to id associated with that reply–the lender— and their contact details. Otherwise, if the inquiry remains unaccepted, we will display the normal inquiry page that displays all of its responses (as long as they haven’t expired). 

Profile Route (/profile):
On the profile page, users can view their own profile with their information and inquiries. Profile can be accessed through both “GET” and “POST” methods. When accessed through “GET”, the route runs three SQL queries. The first query returns the user’s inquiries from the inquiries table ordered by the expiration date in a descending manner. The second query returns the user’s name, username, residential college, and the path to the user’s profile picture in the directory. All of this information is returned into the html template for profile, where the information is displayed in two tables, one for user information and one for the user’s inquiries. Next to each inquiry is a button to “View Replies”, that leads the user to their responses page for the reply. 

If the profile page was accessed via “POST” this means that the user submitted the “Update Profile Picture” form. This form is another pop up modal from Bootstrap that allows the user to upload an image that they want. Like inquiry, the profile route uses the same upload_image function to validate and save the file in order to return a path to the image in the directory. The users table is then updated to change the img_path from the default profile picture into the user’s personal profile picture. 

The profile route and page were implemented so the user can easily see their information and easily view the responses to their inquiries.

Interactions Route (/interactions):
The interactions route is another route that can be accessed through the methods “GET” and “POST.” When accessed through “GET” the left side of the interactions page returns interaction cards for all of the inquiries that the user has responded to, and the right side of the interactions page returns inquiry cards for all of the inquiries that the user has posted. 

For the lending side:
Each card contains the information of the borrower (i.e. name, username, residential college) and the details of their inquiry (i.e. request description, deadline date). It also returns the item picture (if any), the date that the current user wants the item returned by, and the status of the interaction. All information is returned by a query that selects the information from the joined tables of inquiries, responses, interactions, and users. 

The status is color coded, yellow for pending (not started), blue for in progress (borrower has received item), green for completed (borrower has returned item), red for late (borrower did not receive item by their deadline), and red for lost (borrow never returned item to the lender by the return date).

For the borrowing side:
Very similarly to the lending side, each card contains the information of the lender but also the details of the current user’s inquiry. The information for each inquiry is returned by selecting information from the joined tables of inquiries, users, responses, and interactions. 

Dual-User Validation:
This area is where the “POST” method comes in. If the status of the inquiry is “pending”, the user who borrowed the item has a button displayed on their borrowing card in their personal interactions page, asking if they have received the item. When the borrower clicks the button, signaling that they’ve received the item, the status changes to “in progress,” and the user who was the lender in this interaction will now have a button on the lending card of their personal interactions page, asking if the item has been returned. When they confirm that the item has been returned, the status of the overall interaction will change to “completed” and the borrower will now have a button to delete the item. If the borrower deletes the interaction, it is deleted from all tables that deal with the inquiry (inquiries, tags, responses, and interactions).

The verification for all of these buttons are done in the interactions route through “if” statements. 

The route also runs two queries. The first query updates the status of interactions to “late” if the status was “pending” and the expiration date has passed. The second query updates the stays of interactions to “lost” if the status was “in progress” and the lending expiration date has passed. Interactions with these two statuses will not have the delete button to keep the users accountable. 

All of this is done to return a page where the current user can see all of their accepted interactions and keep track of their items. This also hopefully keeps users accountable for the items that they’ve borrowed. 
Front-End Trouble Shooting 

--Text Overflow
Once we had neared the end of the implementation of our final project, group members took turns trying to “break” the code in order to find potential bugs. In doing so, a significant problem that arose was text overflow. In elements like the responses, inquiry cards, profiles, the requests on profiles, and interactions (anything that had the potential to include lengthy text), text would overflow beyond the confines of the page, making it so that users would have to scroll horizontally to see the text in a single line. This also disrupted other CSS elements, causing the original styling to be misaligned to accommodate the single line of lengthy text.

To fix this issue, we modified the CSS on these elements to include a fixed size so that the lengthy text could not go beyond these confines. Additionally, we had to add elements such as scrollbars, overflow-y, and word wrap so that the page could dynamically accommodate these lengthy texts should they be inputted by users, by adding scrollbars if the text exceeds the fixed size that was set, and wrapping the words beyond just a single line.

As for usernames, names, and emails, the same problem arose. Traditionally, username overflow is not solved by adding scrollbars as we did for the other elements, so we based our troubleshooting approach on what is done with other websites—a character limit. And so, we implemented a character limit of 20 in the HTML so that the words did not escape the page in a similar fashion.

--Aesthetic Choices and Accessibility
With our CSS, we wanted to prioritize a visually appealing and accessible user interface. The overall aesthetic is modern and clean, and follows a consistent color scheme that aligns with our overall branding.

Color Palette: The primary colors used are blueish (#223030 and #BBA58F) and white, which creates a professional modern look. This color palette was applied consistently across all pages to make our website look cohesive. 

Accessibility: Accessibility has been a key consideration in the design process. The use of high-contrast colors, such as white text on a dark background, ensures good readability for users with visual impairments. The font sizes and spacing have been carefully chosen to make the content easy to read and navigate.

Additionally, we tried to use color to make the user experience extremely accessible and intuitive. For example, color signifies the status of an interaction (red is lost or late, blue is in progress, yellow is pending, and green is completed), as well as the status of a user's personal interactions on their profile page (green signifying that the interaction completed successfully, and yellow meaning “waiting” for a completed interaction). This helps users easily identify the status of their interactions.

Layout and Structure:
The CSS code establishes a clear and organized layout, with a fixed header and navigation bar, a main content area, and a sticky footer. This layout ensures a consistent user experience across the different pages of the application.

Header: The header includes a fixed background image and a centered site title. The font color on the header still stands out, making it accessible for those with visual impairments. Additionally, the image used works well with the color palette, which maintains our overall aesthetic. 

Navigation Bar: The navigation bar is positioned below the header, which provides easy access to the main sections of the application (Home, Feed, Interactions, and Profile). The navigation links are centered and spaced evenly, making them intuitive to use.

Main Content Area: The main content area is contained within a centered page container with a maximum width of 1400 pixels. This ensures that the content remains readable and visually appealing on a wide range of screen sizes.

Inquiry Cards: The inquiry cards within the Feed section are displayed in a responsive grid layout, with two columns on larger screens and a single column on smaller screens. This layout allows for efficient use of screen space and easy scanning of the available inquiries.

Responsive Design and Mobile Compatibility:
The CSS code includes media queries and responsive design principles to ensure the application looks and functions well on different devices, like mobile phones and desktops. For example, we implemented flexible grid-based layouts, such as the inquiry cards and the interactions/profile sections, that automatically adjust their column count based on the screen size. This ensures that the content remains readable and well-organized.

Additionally, the font sizes and spacing have been defined using relative units (like em and rem) to ensure that the text remains legible and proportional across different screen sizes.

However, in our “best” outcome, our website would have been completely compatible across all devices. While the majority of elements do work across all devices, some aspects, such as filtering, overflow when shown on a smaller screen. Due to time constraints, this was not something that we could properly address. Yet, we still prioritized making sure the bare minimum aspects of our website were compatible, which we were able to achieve.



