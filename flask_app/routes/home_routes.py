# web_app/routes/home_routes.py
import gunicorn 
import psycopg2
import pandas as pd
from flask import Blueprint, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
from flask_app.services.spotify_service import spotify_api_client

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
def index():
    return "Spotify song suggester"


@home_routes.route("/recommendations/<id>")
def recs_from_id(id):
    """
    Takes in a spotify song ID and returns a list of recommended tracks
    as a JSON object using the built-in spotipy recommendations method.
    """

    # sample song id: 6rqhFgbbKwnb9MLmUQDhG6

    sp = spotify_api_client()

    # get the track object based on the input id
    input_track = sp.track(id)

    # get artist uri from the track object
    artist_uri = input_track['artists'][0]['uri']

    recommendations = sp.recommendations(seed_artist=[artist_uri], 
        seed_tracks=[id])['tracks']

    # # Enable code to print list of recommended tracks
    # print('\n recommended tracks')
    # i=1
    # for item in recommendations:
    #     print(i, item, '\n')
    #     i+=1
    
    return jsonify(recommendations)

@home_routes.route("/recommendations/json", methods=['POST'])
def recs_from_json():
    """
    Takes in a spotify track object from a POST request and returns a 
    list of recommended tracks as a JSON object using the built-in spotipy 
    recommendations method.
    """

    sp = spotify_api_client()

    if not request.json:
        return jsonify({"error": "no request received"})

    input_track = request.get_json(force=True)

    input_df = get_features(input_track)

    return jsonify(recommendations)


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


# sample song id: 6rqhFgbbKwnb9MLmUQDhG6

# get the model parameters for a given track
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
    features["sections"] = sections
    features["chorus_hit"] = chorus_hit

    df = pd.DataFrame(features, index=[0])

    return df

#["danceability" ,"energy" ,"key" ,"loudness" ,"mode" ,"speechiness" ,"acousticness" ,"instrumentalness" ,"liveness" ,"valence" ,"tempo" ,"duration_ms" ,"time_signature"]

