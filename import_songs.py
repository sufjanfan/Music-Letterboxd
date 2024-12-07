from cs50 import SQL
import requests
import time

# Initialize the database connection
db = SQL("sqlite:///songs.db")

# Define a function to fetch songs from MusicBrainz API with pagination
def fetch_all_songs():
    base_url = "https://musicbrainz.org/ws/2/recording"
    offset = 0
    limit = 100  # Max limit per request
    all_songs = []

    while True:
        params = {
            "query": "pop",  # You can broaden this query or make it dynamic
            "fmt": "json",
            "offset": offset,
            "limit": limit
        }
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            recordings = data.get("recordings", [])
            if not recordings:
                break  # Exit when no more recordings are found

            all_songs.extend(recordings)
            offset += limit
            time.sleep(1)  # Respect rate limits (adjust if needed)
        else:
            print(f"Failed to fetch songs: {response.status_code}")
            break

    return all_songs

# Populate songs into the database
def populate_songs():
    songs = fetch_all_songs()
    for song in songs:
        title = song.get("title", "Unknown Title")
        artist = song["artist-credit"][0].get("name", "Unknown Artist")
        id = song.get("id")

        try:
            # Insert into the songs table
            db.execute(
                "INSERT OR IGNORE INTO songs (title, artist, id) VALUES (?, ?, ?)",
                title, artist, id
            )
        except Exception as e:
            print(f"Error inserting {title}: {e}")

    print("Songs populated successfully!")

if __name__ == "__main__":
    populate_songs()
