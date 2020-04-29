# data-science

# Flask App 

## Installation

Clone repo into your local machine using https://github.com/bw-ft-spotify-song-suggester-1/data-science.git

Install pipenv with the following packages:
* python-dotenv 
* Requests
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* gunicorn
* spotipy
* psycopg2-binary
* pandas

## Setup
Create a .env file to store the Spotify Api Client ID and the Client Secret.
Run code locally to ensure the routes work.

## Deployment to Heroku
Deploy on Heroku and open the app. If you get a web process error, run "Heroku run pipenv lock" from your terminal.

You must also add Spotify API credentials. Either enter them using commands from the terminal or assign them from your Heroku dashboard.

For the POST request route (/recommendations/json), make sure the JSON uses double quotes. 