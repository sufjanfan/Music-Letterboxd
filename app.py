from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Configure Flask app
app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
db = SQL("sqlite:///songs.db")

# Spotify API credentials
SPOTIPY_CLIENT_ID = "88374e1393b6458790e3cf67005fc5a8"
SPOTIPY_CLIENT_SECRET = "570bec319d274b14a3048a93ad58bb16"

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Homepage
@app.route("/")
def index():
    return render_template("index.html")

'''
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
'''

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error_message = "Must provide both username and password."
            return render_template("login.html", error_message=error_message)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            error_message = "Invalid username or password."
            return render_template("login.html", error_message=error_message)

        session["user_id"] = user[0]["id"]
        return redirect("/profile")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # get form data using post method
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if all fields are provided
        if not username:
            error_message = "Must provide a username."
            return render_template("register.html", error_message=error_message)
        if not password:
            error_message = "Must provide a password."
            return render_template("register.html", error_message=error_message)
        if not confirmation:
            error_message = "Must provide a confirmation."
            return render_template("register.html", error_message=error_message)

        # Check if passwords match
        if password != confirmation:
            error_message = "Passwords do not match."
            return render_template("register.html", error_message=error_message)

        # Hash the password and try to insert the new user
        try:
            hash_password = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)

            # Get the user id from the database (after the insert)
            user = db.execute("SELECT * FROM users WHERE username = ?", username)
            if len(user) != 1:
                error_message = "Something went wrong during registration."
                return render_template("register.html", error_message=error_message)

            # Store user_id in session to log them in
            session["user_id"] = user[0]["id"]

        except ValueError:
            error_message = "Username already exists."
            return render_template("register.html", error_message=error_message)

        return redirect("/profile")

    # go to registration page/form for GET requests
    else:
        return render_template("register.html")


'''
# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("must fill all fields")
        if password != confirmation:
            return apology("passwords do not match")

        hash_pwd = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pwd)
        except:
            return apology("username already exists")

        return redirect("/login")

    return render_template("register.html")
    '''

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Profile
@app.route("/profile")
@login_required
def profile():
    # Get the user details (including the username) based on the session's user_id
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))

    # Check if a user is found
    if len(user) != 1:
        error_message = "Something went wrong during registration."
        return render_template("profile.html", error_message=error_message)

    # Retrieve the username
    username = user[0]["username"]

    reviews = db.execute("SELECT * FROM reviews WHERE user_id = ?", session["user_id"])
    return render_template("profile.html", name=username, reviews=reviews)

'''
@app.route("/review", methods=["POST"])
@login_required
def review():
    try:
        # Retrieve and validate form data
        song_id = request.form.get("song_id")
        review_text = request.form.get("review")
        rating = request.form.get("rating")

        song = db.execute("SELECT id FROM songs WHERE id = ?", song_id)
        if not song:
            error_message = "Song does not exist."
            return render_template("song.html", error_message=error_message)

        if not song_id or not review_text or not rating:
            error_message = "All fields are required."
            return render_template("song.html", error_message=error_message)

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            error_message = "Rating must be a number between 1 and 5."
            return render_template("song.html", error_message=error_message)

        # Insert review into the database
        db.execute(
            "INSERT INTO reviews (user_id, song_id, review, rating) VALUES (?, ?, ?, ?)",
            session["user_id"], song_id, review_text, int(rating)
        )
        return redirect("/profile")

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        error_message = "An error occurred while submitting your review."
        return render_template("profile.html", error_message=error_message)
'''
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # Get song name and artist from the form
        song_name = request.form.get("song_name")
        artist = request.form.get("artist")

        # Validate at least one field is filled
        if not song_name and not artist:
            error_message = "Must provide at least a song name or artist."
            return render_template("search.html", error_message=error_message)

        # Construct query for Spotify search
        query = f"track:{song_name}" if song_name else ""
        if artist:
            query += f" artist:{artist}"

        # Make the API request to Spotify
        results = sp.search(q=query, type="track", limit=10)  # Limit to 10 results

        if results['tracks']['items']:
            songs = results['tracks']['items']

            # Insert each song into the database
            for song in songs:
                song_id = song['id']
                song_title = song['name']
                song_artist = ", ".join([artist['name'] for artist in song['artists']])

                # Use INSERT OR IGNORE to avoid duplicate entries
                db.execute(
                    "INSERT OR IGNORE INTO songs (id, title, artist) VALUES (?, ?, ?)",
                    song_id, song_title, song_artist
                )
        else:
            error_message = "No songs found matching the search."
            return render_template("search.html", error_message=error_message)

        return render_template("search.html", songs=songs)

    # For GET requests, just render the empty search page
    return render_template("search.html")

'''
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # Get song name and artist from the form
        song_name = request.form.get("song_name")
        artist = request.form.get("artist")

        # Validate at least one field is filled
        if not song_name and not artist:
            error_message = "Must provide at least a song name or artist."
            return render_template("search.html", error_message=error_message)

        # Construct query for Spotify search
        query = f"track:{song_name}" if song_name else ""
        if artist:
            query += f" artist:{artist}"

        # Make the API request to Spotify
        results = sp.search(q=query, type="track", limit=10)  # Limit to 10 results

        if results['tracks']['items']:
            songs = results['tracks']['items']
        else:
            error_message = "No songs found matching the search."
            return render_template("search.html", error_message=error_message)

        return render_template("search.html", songs=songs)

    # For GET requests, just render the empty search page
    return render_template("search.html")
'''

@app.route("/song/<song_id>", methods=["GET", "POST"])
def song_details(song_id):
    try:
        # Fetch song details from Spotify API using song_id
        song = sp.track(song_id)

        # Check if the song data is returned as expected
        if not song:
            error_message = "Song not found."
            return render_template("song.html", error_message=error_message)

        # Fetch reviews from your database
        conn = get_db_connection()
        reviews = conn.execute("SELECT reviews.*, users.username FROM reviews JOIN users ON reviews.user_id = users.id WHERE song_id = ?", (song_id,)).fetchall()

        # Handle review submission if it's a POST request
        if request.method == "POST":
            review_text = request.form.get("review")
            rating = request.form.get("rating")

            if not review_text or not rating:
                error_message = "All fields are required."
                return render_template("song.html", error_message=error_message, song=song, reviews=reviews)

            if not rating.isdigit() or not (1 <= int(rating) <= 5):
                error_message = "Rating must be a number between 1 and 5."
                return render_template("song.html", error_message=error_message, song=song, reviews=reviews)

            # Insert review into the database
            conn.execute(
                "INSERT INTO reviews (user_id, song_id, review, rating) VALUES (?, ?, ?, ?)",
                (session["user_id"], song_id, review_text, int(rating))
            )
            conn.commit()

            # Re-fetch the reviews after insertion
            reviews = conn.execute("SELECT reviews.*, users.username FROM reviews JOIN users ON reviews.user_id = users.id WHERE song_id = ?", (song_id,)).fetchall()

        conn.close()

        # Calculate average rating
        ratings = [review["rating"] for review in reviews]
        average_rating = sum(ratings) / len(ratings) if ratings else None

        # Render the song page with the retrieved song and reviews
        return render_template("song.html", song=song, reviews=reviews, average_rating=average_rating)

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        error_message = "An unexpected error occurred while fetching song details."
        return render_template("song.html", error_message=error_message)


'''
@app.route("/song/<song_id>")
def song_details(song_id):
    try:
        # Fetch song details from Spotify API using song_id
        song = sp.track(song_id)

        # Check if the song data is returned as expected
        if not song:
            error_message = "Song not found."
            return render_template("song.html", error_message=error_message)

        # Fetch reviews from your database
        conn = get_db_connection()
        reviews = conn.execute("SELECT reviews.*, users.username FROM reviews JOIN users ON reviews.user_id = users.id WHERE song_id = ?", (song_id,)).fetchall()
        conn.close()

        # Calculate average rating
        ratings = [review["rating"] for review in reviews]
        average_rating = sum(ratings) / len(ratings) if ratings else None

        # Render the song page with the retrieved song and reviews
        return render_template("song.html", song=song, reviews=reviews, average_rating=average_rating)

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        error_message = "An unexpected error occurred while fetching song details."
        return render_template("song.html", error_message=error_message)



@app.route("/song/<song_id>/review", methods=["POST"])
@login_required
def add_review(song_id):
    try:
        # Retrieve and validate form data
        review_text = request.form.get("review")
        rating = request.form.get("rating")

        if not review_text or not rating:
            error_message = "All fields are required."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            error_message = "Rating must be a number between 1 and 5."
            return render_template("song.html", error_message=error_message, song_id=song_id)

        # Insert review into the database
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO reviews (user_id, song_id, review, rating) VALUES (?, ?, ?, ?)",
            (session["user_id"], song_id, review_text, int(rating))
        )
        conn.commit()
        conn.close()

        return redirect(f"/song/{song_id}")

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        error_message = "An error occurred while submitting your review."
        return render_template("song.html", error_message=error_message, song_id=song_id)
'''

@app.route("/recent")
@login_required
def recent():
    reviews = db.execute("SELECT * FROM reviews")
    return render_template("recent.html", reviews=reviews)

@app.route("/like", methods=["POST"])
@login_required
def like_song():
        song_id = request.form.get("song_id")
        if not song_id:
            return jsonify({"error": "Song ID is required"}), 400

        # Check if the song exists
        song = db.execute("SELECT id FROM songs WHERE id = ?", song_id)
        if not song:
            return jsonify({"error": "Song not found"}), 404

        # Insert the like into the database
        db.execute("INSERT OR IGNORE INTO likes (user_id, song_id) VALUES (?, ?)", session["user_id"], song_id)

        return jsonify({"message": "Song liked successfully"}), 200

@app.route("/liked_songs")
@login_required
def liked_songs():
        # Retrieve all liked songs for the current user
        liked_songs = db.execute(
            "SELECT songs.* FROM songs JOIN likes ON songs.id = likes.song_id WHERE likes.user_id = ?",
            session["user_id"]
        )
        return render_template("liked_songs.html", songs=liked_songs)


if __name__ == "__main__":
    app.run(debug=True)
