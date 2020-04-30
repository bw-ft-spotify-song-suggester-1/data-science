# web_app/routes/home_routes.py
import gunicorn 
import psycopg2
import pandas as pd
from flask import Blueprint, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
from flask_app.services.spotify_service import spotify_api_client
from joblib import dump, load
from sklearn import preprocessing

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
def index():
    return "Spotify song suggester"


@home_routes.route("/recommendations/json", methods=['POST'])
def recs_from_json():
    """
    Takes in a spotify track object from a POST request and returns a 
    list of recommended tracks as a JSON object using the built-in spotipy 
    recommendations method.
    """

    sp = spotify_api_client()

    # Check if we got a json object. If we do, assign it to "input_track"
    if not request.json:
        return jsonify({"error": "no request received"})
    
    input_track = request.get_json(force=True)

    # Get the track features needed for the ML model
    input_df = get_features(input_track)

    print("\ninput track dataframe")
    print(input_df.head())

    # Get recommendations. Will be a list of JSON track objects.
    recommendations = get_recommendations(input_df, input_track['uri'])
    
    return recommendations

@home_routes.route("/recommendations/<artist>/<name>")
def recs_from_get(name, artist):
    """
    Takes in an artist name and track name from a GET request and returns a 
    list of recommended tracks as a JSON object using the built-in spotipy 
    recommendations method.
    """

    sp = spotify_api_client()

    # Use search query to get the track id
    # This assumes that there is only one entry for a Artist + Song pair
    
    
    # TODO
    """
    make sure query works for a given song + artist

    Figure out the format of returned results from the query

    Figure out how to get song uri from the query results

    takee song uri, pass it into the function to convert to dataframe

    throw into model

    return results as a list of crap
    """

    input_track = sp.search(q='artist:' + artist + ' track:' + name,
        type='track',limit=1)
    
    return input_track

    for item in input_track:
        print(item)

    # Get the track features needed for the ML model
    input_df = get_features(input_track)

    print("\ninput track dataframe")
    print(input_df.head())

    # Get recommendations. Will be a list of JSON track objects.
    recommendations = get_recommendations(input_df, input_track['uri'])
    
    return recommendations

@home_routes.route("/recommendations/test/json", methods=['POST'])
def recs_from_json_test():
    """
    Takes in a spotify track object from a POST request and returns a 
    list of recommended tracks as a JSON object using the built-in spotipy 
    recommendations method.
    """

    sp = spotify_api_client()

    if not request.json:
        return jsonify({"error": "no request received"})

    input_track = request.get_json(force=True)

    # get the artist uri and track id
    artist_uri = input_track['artists'][0]['uri']
    track_id = input_track['id']
    
    # use built-in recommendations method to get a list of recommended track objects
    recommendations = sp.recommendations(seed_artist=[artist_uri], 
        seed_tracks=[track_id])['tracks']

    return jsonify(recommendations)


@home_routes.route("/audio-features")
def audio_feat():
    """
    Get audio features for a given track uri.
    """

    sp = spotify_api_client()
    tracky_uri = 'spotify:track:6MjiVEJy1YVuJNFu72OH61'
    results = sp.audio_features(tracks=tracky_uri)
    for r in results:
        return jsonify(r)

@home_routes.route("/get_track/<id>")
def get_track(id):
    """Get track object for a given track id"""
    sp = spotify_api_client()
    track = sp.track(id)

    print_track_object(track)

    return track


def get_features(input_track):
    """
    Takes a JSON track object, and returns a dataframe containing the features
    used in the ML model.
    """

    sp = spotify_api_client()

    track_id = input_track['id']
    audio_analysis = sp.audio_analysis(track_id)
    audio_features = sp.audio_features(track_id)[0]

    # Add info from Spotify API "audio_analysis" call:
    # sections: # of sections in the song (Verse 1, Chorus 1, Bridge, etc.)
    # chorus_hit: when the first chorus starts in the song (second mark in track)
    sections = len(audio_analysis['sections'])
    chorus_hit = audio_analysis['sections'][2]['start']

    # Create dictionary containing only the values we want from the audio features
    keys = ["danceability" ,"energy" ,"key" ,"loudness" ,"mode" ,"speechiness" ,
    "acousticness" ,"instrumentalness" ,"liveness" ,"valence" ,"tempo" ,
    "duration_ms" ,"time_signature"]
    features = {key: audio_features[key] for key in keys}

    # add the audio analysis features
    features["chorus_hit"] = chorus_hit
    features["sections"] = sections

    # convert to dataframe object
    df = pd.DataFrame(features, index=[0])

    return df


def get_40k_spotify_songs():
    """
    Function to get and return a dataset of 40k Spotify songs, so we can
    use our k-NN model to pick which Spotify songs to recommend to the user:
    """

    # Get data (all):
    dataset00 = pd.read_csv(r'https://docs.google.com/spreadsheets/d/e/2PACX-1vSFqeUFGZwH52bU-IepHfp2xRD3A0asGpGJRd3jaJYA4PwAmUju-5CmnepyBAvc64rY6gXwn2nUQG0e/pub?output=csv')
    dataset10 = pd.read_csv(r'https://docs.google.com/spreadsheets/d/e/2PACX-1vR-Sc2ksuQCaZmH_Hy90bhCCP13AOVlBFAMRNwVYgEcT3RO-0UimxD9Loi5KVDOnurxvBoteW-whOWp/pub?output=csv')
    dataset60 = pd.read_csv(r'https://docs.google.com/spreadsheets/d/e/2PACX-1vTPxGmOZVXdAYr2D5_ml_3YRXorUVarxlTQ4bYzews8YXWSY8ArdFAyxffvm8gmI-FxMr_8vJtCK_Y-/pub?output=csv')
    dataset70 = pd.read_csv(r'https://docs.google.com/spreadsheets/d/e/2PACX-1vTINdcUA6cKJyHJS76NrcXPLbX_jFjt5S4pNIdAKw-4GF1w8ngBeorLrAPEYxSqgnxE9MybmzQ9NYXK/pub?output=csv')
    dataset80 = pd.read_csv(r'https://docs.google.com/spreadsheets/d/e/2PACX-1vR5LNcY8trkxu8vIJHf8Ha0vDO9Xz2k2M7UCdEGhaJxz9vnB_SqET9fy88icZwIjPKeK8USi05_0zii/pub?output=csv')
    dataset90 = pd.read_csv(r'https://docs.google.com/spreadsheets/d/e/2PACX-1vRFUiB5RX_2qMQuZSuP-u_wQvjqlaSOTeKY4uGjwfeoGTgZUCesq46xlYjLqi4vmN-VQ4zK0Zm-jXmw/pub?output=csv')

    frames = [dataset60, dataset70, dataset80, dataset90, dataset00, dataset10]
    spotify_songs_df = pd.concat(frames, ignore_index=True)

    spotify_songs_df = spotify_songs_df.drop(['target'], axis=1)
    spotify_songs_df = spotify_songs_df.drop_duplicates("uri")

    spotify_songs_df_uris = spotify_songs_df['uri']

    return spotify_songs_df, spotify_songs_df_uris


def get_recommendations(track_df, track_uri):
    """
    Given a pandas dataframe of track features and associateed track uri,
    use ML model to generate recommendations. 
    Returns list of JSON track objects.
    """
    
    sp = spotify_api_client()

    # Get dataset of Spotify songs for kNN:
    spotify_songs_df, spotify_songs_df_uris = get_40k_spotify_songs()
    X_train = spotify_songs_df.drop(['track', 'artist',  'uri'], axis=1)

    # Instantiate our scaler for standardizing data (z-scores):
    scaler = preprocessing.StandardScaler().fit(X_train)

    # Array of only the values of input_track_df_ordered:
    input_values_only = track_df.loc[0].values

    # # Standardize (z-scores) our input values before inputting into model:
    input_values_only = scaler.transform([input_values_only])

    # Load our ML model from compressed joblib file:
    model_knn = load('model.joblib')

    # Get recommended songs from our model:
    output_values, output_uris = model_knn.kneighbors(input_values_only)
    output_values = output_values[0]
    output_uris = output_uris[0]

    # List of Spotify URIs for the songs our model recommended
    # Checks if any recommended track is the same as the input track
    # (to query the Spotify API --> get their full track objects):

    # TODO
    """
    figure out how to get to this info for each recommended track:

    { 
    name: "", (this is the song name)
    uri: "",
    artist: "",
    album: "",
    spotify_id: "",
    popularity: (number from 0-100),
    preview_url: "",
    image: ""
    }

    append to our list of recommendations 
    return list
    """

    recs_uris = []
    for uri_index in output_uris:
        song_uri = spotify_songs_df_uris[uri_index]
        
        if song_uri == track_uri:
            pass
        
        else:
            recs_uris.append(song_uri)
            print("uri", song_uri)

    # Get JSON of the full Spotify API "track objects" for the songs:
    recs = sp.tracks(recs_uris)

    return recs


def get_track_info(track):
    """
    Given a track object, return a dictionary of track name, track artist,
    and album name. Used for testing and troubleshooting.
    """
    # Remember that artist and album artist have different entries in the
    # spotify track object.

    name = track["name"]
    artist = track['artists'][0]['name']
    album = track['album']['name']
    return {"name":name, "artist":artist, "album":album}


def print_track_object(track):
    """
    Given a track object, print its contents in a more readable format.
    Trouble shooting function. Does not return anything.
    """
        
    for key in track:
        print("\nKEY:", key)

        if isinstance(track[key], dict)==True:
            for subkey in track[key]:
                print("\tSUBKEY", subkey, "\t", track[key][subkey])

        elif isinstance(track[key], list)==True:
            for item in track[key]:
                print("\tLIST_ITEM:\t", item)
        
        else:
            print("\tENTRY:", track[key])

