Documentation for your project in the form of a Markdown file called README.md. This documentation is to be a user’s manual for your project. Though the structure of your documentation is entirely up to you, it should be incredibly clear to the staff how and where, if applicable, to compile, configure, and use your project. Your documentation should be at least several paragraphs in length. It should not be necessary for us to contact you with questions regarding your project after its submission. Hold our hand with this documentation; be sure to answer in your documentation any questions that you think we might have while testing your work.

Welcome to Musicboxd!

This website allows users to create an account that serves as their "music box", storing their ratings and reviews of any songs they log. The website can be launched by typing "flask run" into the terminal (once in the correct directory for the project) and following the link generated.

Upon accessing the website, the user will see a screen welcoming them to Musicboxd, with buttons that allow them to log in or register for an account. If this is the user's first time using the website, they should press the "Register" button to create an account. When the user presses "Register", they will be prompted to input a username and a password, and then to confirm the password. If the username is already in use, the user will be notified and should choose a different username. When the user successfully creates an account, they will be brought to their profile.

The profile displays the user's 5 most recent liked songs and their 5 most recent reviews. If the user has just created an account, both sections for liked songs and reviews should indicate that there are no liked songs and no reviews yet. If the user would like to see a complete list of their liked songs or their reviews, they can follow the links at the bottom of each section (these links read "View All Liked Songs" and "View All Reviews"). Alternatively, the user can go to the navbar at the top of the page and click on "Your Liked Songs" or "Your Reviews". To log out of their account, the user can press the "Log Out" button on the right side of the navbar. (Clicking on the Musicboxd logo on the left side of the navbar will bring the user to a "front page" that prompts them to visit their profile, which can be done by clicking the button in the middle of the page or clicking on "Profile" in the navbar.)

To log a song, the user should navigate to the navbar and click on "Song Search". This screen shows text boxes where the user an input a song name and/or a musical artist to search for the song they would like to log. At least one of the fields must be filled in order to execute a successful search, but the user is able to search by only inputting a song title or an artist. The search results that populate below the text boxes only show the top 10 matches for the search query, so the user may find the most success in locating their desired song if they fill in both fields of the search. The search results appear in a table that displays the song title, the artist, and links to listen to the song on Spotify or add a review of the song. The user can click on the link that reads "Add Review" in the row corresponding to the song they would like to review in order to log the song.

Clicking this link brings the user to a page displaying the title of the song, as well as other information about the song. Below the title of the song, there is a heart icon that the user can use to "like" the song. If the user clicks on the heart icon, it will change color to indicate that the song has been liked, and the song's information will be added to the user's profile and liked songs database. To remove the like from the song, the user can click the heart icon again and it will turn gray. Below the heart icon, the website provides information about the artist of the song and the album it is on. Below this information is a line that provides the average rating of the song across all users of the website.

Below this introductory information, the user will see a row of stars and a text box that allows them to submit a review and a rating of the song. The user can select the number of stars, out of 5, that corresponds to their desired rating. Hovering over the stars will cause them to change color according to the position of the user's mouse. The user can click in the text box to write their review--if the length of the review exceeds the size of the text box, a scroll bar will appear to allow the user to see the entirety of the review. The text box can also be resized vertically to show the entire review without a scroll bar. When all of this information has been completed, the user can click the "Submit Review" button to log the song. Below this section for submitting the reviews, the user can also see reviews and ratings of the song from other users. After the review has been submitted, the page will automatically update to include the user's review (the average rating will reflect the user's rating and the "Community Reviews" section will display the user's review, which shows their username, their written review, their rating, and the timestamp at which they submitted the review). At this point, navigating back to the "Profile" page (which can be done through the navbar at the top) will also show the new review. Users are able to submit reviews for the same song as many times as they would like--each review will show the timestamp at which it was submitted.

The navbar also includes a page for recent community reviews, which can be accessed by clicking on "Community Reviews" on the navbar. This page shows recent reviews from all members of the community. The reviews are organized into cards, each of which shows the song reviewed, the artist's name, the reviewer's username, the reviewer's written review and rating, and the timestamp at which the review was submitted.

Once the user has logged their first review, they can return to their profile to see that they are able to unlike the song and edit or delete their review. 
