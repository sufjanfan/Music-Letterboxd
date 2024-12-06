from flask import Flask, render_template, redirect, request, session, flash
from flask_session import Session
from cs50 import SQL
from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///songs.db")

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q")
    if query:
        # Perform a case-insensitive search in the database
        songs = db.execute(
            "SELECT * FROM songs WHERE title LIKE ? OR artist LIKE ?",
            f"%{query}%",
            f"%{query}%"
        )
    else:
        songs = None  # No search query, so no songs to display

    return render_template("index.html", songs=songs)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return apology("must provide username and password")

        hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            return apology("username already exists")

        flash("Registered!")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return apology("invalid username and/or password")

        session["user_id"] = user[0]["id"]
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/rate", methods=["POST"])
@login_required
def rate():
    song_id = request.form.get("song_id")
    rating = request.form.get("rating")
    review = request.form.get("review")

    db.execute("INSERT INTO reviews (user_id, song_id, rating, review) VALUES (?, ?, ?, ?)",
               session["user_id"], song_id, rating, review)
    flash("Review added!")
    return redirect("/")

@app.route("/profile/<username>")
@login_required
def profile(username):
    user = db.execute("SELECT * FROM users WHERE username = ?", username)
    if len(user) != 1:
        return apology("user not found")

    reviews = db.execute("SELECT * FROM reviews WHERE user_id = ?", user[0]["id"])
    return render_template("profile.html", user=user[0], reviews=reviews)

if __name__ == "__main__":
    app.run(debug=True)
