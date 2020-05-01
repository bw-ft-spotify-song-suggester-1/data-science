# data-science

## Spotify song suggester 
Model - K-Nearest Neighbors 
Wrapper - Spotipy - https://spotipy.readthedocs.io/en/2.12.0/

# Flask App 
Designed to fetch data from the Spotify API https://developer.spotify.com/documentation/web-api/reference/ and send JSON to web app.

## Installation

Clone the data science repo into your local machine using https://github.com/bw-ft-spotify-song-suggester-1/data-science.git

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
* joblib
* sklearn

## Setup
Create a .env file to store the Spotify Api Client ID and the Client Secret.
Run code locally to ensure the routes work.

## Deployment to Heroku
Deploy on Heroku and open the app. If you get a web process error, run "Heroku run pipenv lock" from your terminal.

You must also add Spotify API credentials. Either enter them using commands from the terminal or assign them from your Heroku dashboard.

For the POST request route (/recommendations/json), make sure the JSON uses double quotes. 

# Contributions
## Unit 3 - Data Engineers
Adewale Adeagbo - Implemented flask app architecture; and specified neccessary Spotify API endpoints.Tested and wrote reproducible scripts for routes/API relevant to data science functionality. Implemented pickled NN model. Documented web app product vision. 

## Unit 4 - Machine Learning Engineers
Adriann Lefebvere - Tested neural network architectures and created a working NearestNeighbor model for the flask app to use. Created instructions for the data engineers to use to help them get started with implementing the pickled model onto the flask app.

Ryan Mecking - Tested and iterated ML and NN models to be pickled then implemented into flask app. 