from cs50 import SQL
import requests

# Initialize the database connection
db = SQL("sqlite:///songs.db")

def fetch_songs():
    # Fetch songs from MusicBrainz API
    response = requests.get("https://musicbrainz.org/ws/2/recording?query=pop&fmt=json")
    if response.status_code == 200:
        return response.json().get("recordings", [])
    return []

def populate_songs():
    songs = fetch_songs()
    for song in songs:
        title = song["title"]
        artist = song["artist-credit"][0]["name"]
        id = song["id"]  # Extract the track ID
        try:
            # Insert into the songs table
            db.execute(
                "INSERT INTO songs (title, artist, track_id) VALUES (?, ?, ?)",
                title, artist, id
            )
        except Exception as e:
            print(f"Error inserting {title}: {e}")
    print("Songs populated successfully!")

if __name__ == "__main__":
    populate_songs()
