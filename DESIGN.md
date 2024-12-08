A “design document” for your project in the form of a Markdown file called DESIGN.md that discusses, technically, how you implemented your project and why you made the design decisions you did. Your design document should be at least several paragraphs in length. Whereas your documentation is meant to be a user’s manual, consider your design document your opportunity to give the staff a technical tour of your project underneath its hood.

Musicboxd is a Flask web application that contains Spotify API integrations for searching, reviewing, and liking songs. It utilizes a SQLite database to store user, song, and review information and supports features like user authentication (login, registration), adding reviews and ratings for songs, and liking/unliking songs.

User authentication: 
