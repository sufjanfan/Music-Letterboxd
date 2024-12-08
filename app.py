from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheFileHandler

# initialize Flask app
app = Flask(__name__)

# configure session to use for storage
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configures sql database with the four tables used throughout the code
db = SQL("sqlite:///songs.db")

# sets up a cache to avoid using a file
cache_handler = spotipy.cache_handler.MemoryCacheHandler()

# configures Spotify API with client credentials from Spotify dev dashboard
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="88374e1393b6458790e3cf67005fc5a8",
    client_secret="570bec319d274b14a3048a93ad58bb16",
    cache_handler=cache_handler  # disables file caching by using memory cache
))

def get_db_connection():
    conn = sqlite3.connect('songs.db')  # connects to songs.db
    conn.row_factory = sqlite3.Row  # gives access to columns by name
    return conn

# renders homepage
@app.route("/")
def index():
    return render_template("index.html")

# login page -- allows users toenter their username and password and redirects to profile when finished
@app.route("/login", methods=["GET", "POST"])
def login():
# handles user login
    # retrieves user inputs to form
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # validates user input
        if not username or not password:
            error_message = "Must provide both username and password."
            return render_template("login.html", error_message=error_message)

        # queries the database for the user
        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # checks if credentials are correct
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            error_message = "Invalid username or password."
            return render_template("login.html", error_message=error_message)

        # stores user ID in session
        session["user_id"] = user[0]["id"]

        # returns to the user's profile
        return redirect("/profile")

    # for get requests, render login page
    return render_template("login.html")

# registration page -- users can sign up for an account here
@app.route("/register", methods=["GET", "POST"])
def register():
# register user
    # retrieves user inputs using post method
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # validates input fields
        if not username:
            error_message = "Must provide a username."
            return render_template("register.html", error_message=error_message)
        if not password:
            error_message = "Must provide a password."
            return render_template("register.html", error_message=error_message)
        if not confirmation:
            error_message = "Must provide a confirmation."
            return render_template("register.html", error_message=error_message)

        # makes sure password confirmation matches
        if password != confirmation:
            error_message = "Passwords do not match."
            return render_template("register.html", error_message=error_message)

        # hashes the password and tries to insert the new user into users table
        try:
            hash_password = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)

            # retrieves the user id from the database
            user = db.execute("SELECT * FROM users WHERE username = ?", username)
            if len(user) != 1:
                error_message = "Something went wrong during registration."
                return render_template("register.html", error_message=error_message)

            # stores user_id in session to log them in
            session["user_id"] = user[0]["id"]

        except ValueError:
            error_message = "Username already exists."
            return render_template("register.html", error_message=error_message)

        return redirect("/profile")

    # for get requests, render registration page
    else:
        return render_template("register.html")

# logout route
@app.route("/logout")
def logout():
    # clears the session
    session.clear()
    return redirect("/")

# profile route
@app.route("/profile")
@login_required
def profile():
    # retrieve the user's details based on the session's user_id
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))

    if len(user) != 1:
        error_message = "Something went wrong during registration."
        return render_template("profile.html", error_message=error_message)

    # retrieve the username
    username = user[0]["username"]

    #retrieve user reviews from database
    reviews = db.execute(
        """
        SELECT reviews.id, reviews.rating, reviews.timestamp, reviews.review,
        songs.title AS song_title, songs.artist AS song_artist
        FROM reviews
        JOIN songs ON reviews.song_id = songs.id
        WHERE reviews.user_id = ?
        ORDER BY reviews.timestamp DESC LIMIT 5
        """, session["user_id"]
        )

    # retrieve user's liked songs
    liked_songs = db.execute(
        """
        SELECT songs.id AS spotify_id, songs.title AS name, songs.artist
        FROM songs
        JOIN likes ON songs.id = likes.song_id
        WHERE likes.user_id = ?
        ORDER BY likes.timestamp DESC LIMIT 5

        """,
        (session["user_id"],)
    )

    # render profile page with user, review, and liked songs data
    return render_template("profile.html", name=username, reviews=reviews, songs=liked_songs)

# search for songs
@app.route("/search", methods=["GET", "POST"])
def search():
    # retrieve desired song name and artist from the form
    if request.method == "POST":
        song_name = request.form.get("song_name")
        artist = request.form.get("artist")

        # confirm that at least one field is filled
        if not song_name and not artist:
            error_message = "Must provide at least a song name or artist."
            return render_template("search.html", error_message=error_message)

        # create query for Spotify search
        query = f"track:{song_name}" if song_name else ""
        if artist:
            query += f" artist:{artist}"

        # use Spotify API to search for songs
        results = sp.search(q=query, type="track", limit=10)  # Limit to 10 results

        # check if results were found
        if results['tracks']['items']:
            songs = results['tracks']['items']

            # insert song details into the database
            for song in songs:
                song_id = song['id']
                song_title = song['name']
                song_artist = ", ".join([artist['name'] for artist in song['artists']])

                # use INSERT or IGNORE to prevent duplicates
                db.execute(
                    "INSERT OR IGNORE INTO songs (id, title, artist) VALUES (?, ?, ?)",
                    song_id, song_title, song_artist
                )
        else:
            error_message = "No songs found matching the search."
            return render_template("search.html", error_message=error_message)

        return render_template("search.html", songs=songs)

    # for GET requests, render the empty search page
    return render_template("search.html")

# song details route
@app.route("/song/<song_id>", methods=["GET", "POST"])
def song_details(song_id):
    try:
        # retrieve song details from Spotify API using song_id
        song = sp.track(song_id)

        # check if song exists
        if not song:
            error_message = "Song not found."
            return render_template("song.html", error_message=error_message)

        # cehck if the song was already liked by the user
        liked_song = db.execute(
            "SELECT * FROM likes WHERE user_id = ? AND song_id = ?",
            session["user_id"], song_id
        )

        liked_status = True if liked_song else False

        # fetch reviews
        conn = get_db_connection()
        reviews = conn.execute(
            "SELECT reviews.*, users.username FROM reviews JOIN users ON reviews.user_id = users.id WHERE song_id = ?",
            (song_id,)
        ).fetchall()
        conn.close()

        # add review if it's a POST request
        if request.method == "POST":
            review_text = request.form.get("review")
            rating = request.form.get("rating")

            if not review_text or not rating:
                error_message = "All fields are required."
                return render_template("song.html", error_message=error_message, song=song, reviews=reviews)

            if not rating.isdigit() or not (1 <= int(rating) <= 5):
                error_message = "Rating must be a number between 1 and 5."
                return render_template("song.html", error_message=error_message, song=song, reviews=reviews)

            # see if the user has already reviewed this song
            conn = get_db_connection()
            existing_review = conn.execute(
                "SELECT * FROM reviews WHERE user_id = ? AND song_id = ?",
                (session["user_id"], song_id)
            ).fetchone()

            # insert review into the database
            conn = get_db_connection()
            conn.execute(
                    "INSERT INTO reviews (review, rating, user_id, song_id, timestamp) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    (review_text, int(rating), session["user_id"], song_id)
                )
            conn.commit()
            conn.close()

            # re-fetch the reviews after insertion
            conn = get_db_connection()
            reviews = conn.execute(
                """SELECT reviews.*, users.username FROM reviews
                JOIN users ON reviews.user_id = users.id
                WHERE song_id = ?
                ORDER BY reviews.timestamp DESC""",
                (song_id,)
            ).fetchall()
            conn.close()

        # calculate average rating of song
        ratings = [review["rating"] for review in reviews]
        average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        # render the song page with the retrieved song and reviews
        return render_template("song.html", song=song, reviews=reviews, average_rating=average_rating, liked_status=liked_status)

    except Exception as e:
        print(f"Error: {e}")  # debugging
        error_message = "An unexpected error occurred while fetching song details."
        return render_template("song.html", error_message=error_message)


@app.route("/song/<song_id>/review", methods=["POST"])
@login_required
def add_review(song_id):
    try:
        # retrieve song details from Spotify API
        song = sp.track(song_id)

        # retrieve and validate form data
        review_text = request.form.get("review")
        rating = request.form.get("rating")

        if not review_text or not rating:
            error_message = "All fields are required."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            error_message = "Rating must be a number between 1 and 5."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        # put review into the database associated with song and user id
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO reviews (review, rating, user_id, song_id, timestamp) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (review_text, int(rating), session["user_id"], song_id)
        )
        conn.commit()
        conn.close()

        return redirect(f"/song/{song_id}")

    except Exception as e:
        print(f"Error: {e}")  # debugging
        error_message = "An error occurred while submitting your review."
        return render_template("song.html", error_message=error_message, song_id=song_id)


@app.route("/recent")
@login_required
def recent():
    #retrieves username, rating, timestamp, content, title & artist of song
    reviews = db.execute("""
        SELECT users.username, reviews.rating, reviews.timestamp, reviews.review,
               songs.title AS song_title, songs.artist AS song_artist
        FROM reviews
        JOIN users ON reviews.user_id = users.id
        JOIN songs ON reviews.song_id = songs.id
        ORDER BY reviews.timestamp DESC
    """)
    # renders recent reviews template with all reviews ordered by recency
    return render_template("recent.html", reviews=reviews)

@app.route("/like", methods=["POST"])
@login_required
def like_song():
    try:
        song_id = request.form.get("song_id")

        if not song_id:
            error_message = "Song ID required."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        # makes sure song exists
        song = db.execute("SELECT id FROM songs WHERE id = ?", song_id)
        if not song:
            error_message = "Song not found."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        # check if the song has already been liked by the user
        already_liked = db.execute(
            "SELECT * FROM likes WHERE user_id = ? AND song_id = ?",
            session["user_id"], song_id
        )

        if len(already_liked) == 0:
            # if not liked yet, add the song to likes
            db.execute("INSERT INTO likes (user_id, song_id) VALUES (?, ?)", session["user_id"], song_id)
            liked = True
        else:
            # if already liked, remove it from likes
            db.execute("DELETE FROM likes WHERE user_id = ? AND song_id = ?", session["user_id"], song_id)
            liked = False
        return jsonify({"liked": liked})

    except Exception:
        error_message = "Error in liked song."
        return render_template("song.html", error_message=error_message, song_id=song_id)

@app.route("/all_liked")
@login_required
def all_liked():
    # display list of all of the user's liked songs in order of recency
    liked_songs = db.execute(
        """
        SELECT songs.id AS spotify_id, songs.title AS name, songs.artist
        FROM songs
        JOIN likes ON songs.id = likes.song_id
        WHERE likes.user_id = ?
        ORDER BY likes.timestamp DESC
        """,
        (session["user_id"],)
    )
    return render_template("liked_songs.html", songs=liked_songs)


@app.route("/all_reviews")
@login_required
def all_reviews():
    # retrieve user's reviews (joining reviews and songs table)
    reviews = db.execute(
        """
        SELECT reviews.id, reviews.rating, reviews.timestamp, reviews.review,
            songs.title AS song_title, songs.artist AS song_artist
        FROM reviews
        JOIN songs ON reviews.song_id = songs.id
        WHERE reviews.user_id = ?
        ORDER BY reviews.timestamp DESC
        """,
        (session["user_id"],)
    )
    # renders all_reviews.html with reviews data
    return render_template("all_reviews.html", reviews=reviews)


@app.route("/delete_review/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    try:
        # Ensure the review belongs to the logged-in user
        review = db.execute("SELECT * FROM reviews WHERE id = ? AND user_id = ?", review_id, session["user_id"])
        if not review:
            error_message = "Review not found."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        # Delete the review
        db.execute("DELETE FROM reviews WHERE id = ?", review_id)

        # Redirect to the reviews page
        return redirect("/profile")

    except Exception:
        error_message = "An error occurred while deleting your review."
        return render_template("profile.html", error_message=error_message, song_id=song_id)

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    try:
        # Fetch the review along with the associated song's title and artist
        review = db.execute("""
            SELECT reviews.*, songs.title AS song_title, songs.artist AS song_artist
            FROM reviews
            JOIN songs ON reviews.song_id = songs.id
            WHERE reviews.id = ? AND reviews.user_id = ?
        """, review_id, session["user_id"])

        if not review:
            error_message = "An error occurred while editing your review."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        # For GET request, display the review in a form
        if request.method == "GET":
            return render_template("edit_review.html", review=review[0])

        # For POST request, update the review in the database
        new_review = request.form.get("review")
        new_rating = request.form.get("rating")

        # Validate input
        if not new_review or not new_rating:
            error_message = "All fields are required."
            return render_template("edit_review.html", review=review[0], error_message=error_message)

        if not new_rating.isdigit() or not (1 <= int(new_rating) <= 5):
            error_message = "Rating must be a number between 1 and 5."
            return render_template("edit_review.html", review=review[0], error_message=error_message)

        # Update the review
        db.execute(
            "UPDATE reviews SET review = ?, rating = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
            new_review, int(new_rating), review_id
        )

        return redirect("/profile")

    except Exception:
        error_message = "An error occurred while editing your review."
        return render_template("profile.html", error_message=error_message)


if __name__ == "__main__":
    app.run(debug=True)

