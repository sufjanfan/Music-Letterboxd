import os
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import requests

# Configure Flask app
app = Flask(__name__)


# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
db = SQL("sqlite:///songs.db")

# Homepage
@app.route("/")
def index():
    return render_template("index.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("must provide username and password")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return apology("invalid username or password")

        session["user_id"] = user[0]["id"]
        return redirect("/profile")

    return render_template("login.html")

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

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        query = request.form.get("query")
        response = requests.get(f"https://musicbrainz.org/ws/2/recording/?query={query}&fmt=json")
        if response.status_code != 200:
            return apology("MusicBrainz API error")

        songs = response.json().get("recordings", [])
        return render_template("profile.html", songs=songs)

    reviews = db.execute("SELECT * FROM reviews WHERE user_id = ?", session["user_id"])
    return render_template("profile.html", reviews=reviews)

# Add Review
@app.route("/review", methods=["POST"])
@login_required
def review():
    song_title = request.form.get("title")
    review_text = request.form.get("review")
    rating = request.form.get("rating")

    if not song_title or not review_text or not rating:
        return apology("must fill all fields")

    db.execute(
        "INSERT INTO reviews (user_id, title, review, rating) VALUES (?, ?, ?, ?)",
        session["user_id"], song_title, review_text, rating
    )
    return redirect("/profile")

if __name__ == "__main__":
    app.run(debug=True)
