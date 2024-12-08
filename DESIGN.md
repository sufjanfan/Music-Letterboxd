A “design document” for your project in the form of a Markdown file called DESIGN.md that discusses, technically, how you implemented your project and why you made the design decisions you did. Your design document should be at least several paragraphs in length. Whereas your documentation is meant to be a user’s manual, consider your design document your opportunity to give the staff a technical tour of your project underneath its hood.

Musicboxd is a Flask web application that contains Spotify API integrations for searching, reviewing, and liking songs. It utilizes a SQLite database to store user, song, and review information and supports features like user authentication (login, registration), adding reviews and ratings for songs, and liking/unliking songs.

User authentication includes a few different paths. Registration (/register) allows users to sign up by providing a username, password, and confirmation password. Passwords are hashed using werkzeug.security to securely store them. Error messages are returned as a popup if the username is already in use, the password and confirmation don't match, or any of the 3 fields aren't filled out. We chose to use a popup instead of a completely new error response page in order to make the process as seamless as possible. If the user instead wants to sign
    Login (/login): Users can log in with their username and password. If the credentials are correct, they are redirected to their profile page.
    Logout (/logout): Clears the session and redirects to the home page.

SQL: There are four tables stored in songs.db that hold the user's data: users, songs, likes, and reviews. Users holds every user's id (which serves as the primary key), username, and password hash generated via werkzeug.security.Songs,


Profile (/profile):

Displays user details and their reviews, including the songs they've liked (from the likes table) and the songs they've reviewed (from the reviews table).
Song Search (/search):

Allows users to search for songs on Spotify based on a song name and artist. The search is performed via the Spotify API, and the results are stored in the songs table in the SQLite database.
Song Details (/song/<song_id>):

Shows details of a specific song, including a review section where users can submit their own reviews and ratings.
The song's liked status is checked, and users can toggle this (i.e., "like" or "unlike" the song).
Reviews are stored and displayed, and the average rating for the song is calculated.
Like/Unlike Songs (/like):

Allows users to "like" or "unlike" a song. This is handled with a POST request, which checks whether the song has already been liked by the user and toggles the status accordingly.
All Liked Songs (/all_liked):

Displays a list of all songs liked by the user.
All Reviews (/all_reviews):

Displays all reviews submitted by the user.
Review Management (/edit_review, /delete_review):

Users can edit and delete their reviews for songs.
