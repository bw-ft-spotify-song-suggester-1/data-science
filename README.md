# data-science

## Spotify song suggester 
Model - K-Nearest Neighbors 

# Flask App 
Designed to process spotify tracks from incoming POST requests, fetch data from the Spotify API https://developer.spotify.com/documentation/web-api/reference/, and return song suggestions using a machine learning model.

## Installation

Clone the data science repo into your local machine using https://github.com/bw-ft-spotify-song-suggester-1/data-science.git

Install pipenv with the following packages:
* flask
* gunicorn
* joblib
* pandas
* psycopg2-binary
* python-dotenv 
* requests
* sklearn
* spotipy

## Setup
Create a .env file to store the Spotify Api Client ID and the Client Secret.
Run code locally to ensure the routes work. All POST requests should send input data as JSON objects.

## Deployment to Heroku
Deploy on Heroku and open the app. If you get a web process error, running "Heroku run pipenv lock" from your terminal may fix it. Alternatively, use a requirements text file in lieu of a pipfile.

You must also add Spotify API credentials. Either enter them using commands from the terminal or assign them from your Heroku dashboard.

For the POST request routes, using single quotes for the input JSON objects may cause errors.

# Contributions
## Unit 3 - Data Engineers
Adewale Adeagbo - Implemented flask app architecture; and specified neccessary Spotify API endpoints.Tested and wrote reproducible scripts for routes/API relevant to data science functionality. Implemented pickled NN model. Documented web app product vision. 

Harrison Kang - Implemented flask app archirecture. Set up multiple app routes to handle GET and POST requests with different data objects. Deployed app to Heroku cloud platform. Integrated ML model into flask app. Implemented a data pipeline to take song information in various formats, generate recommendations, and output them to the front end in an appropriate format.

## Unit 4 - Machine Learning Engineers
Adriann Lefebvere - Tested neural network architectures and created a working NearestNeighbor model for the flask app to use. Created instructions for the data engineers to use to help them get started with implementing the pickled model onto the flask app.

Ryan Mecking - Tested and iterated ML and NN models to be pickled then implemented into flask app. 