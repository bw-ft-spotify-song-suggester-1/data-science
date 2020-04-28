# web_app/routes/home_routes.py

from flask import Blueprint, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
from flask_app.services.spotify_service import spotify_api_client

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
def index():
    return "Spotify song suggester"

@home_routes.route("/artist")
def artist_profile():
    """
    Get artist from spotify with the assigned uri.
    """
    sp = spotify_api_client()
    artist_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
    results = sp.artist(artist_id=artist_uri)
    return results

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

@home_routes.route("/album-list")
def album_list():
    """
    Get list of albums for a given artist uri.
    """

    sp = spotify_api_client()
    birdy_uri ='spotify:artist:2WX2uTcsvV5OnS0inACecP'
    results = sp.artist_albums(artist_id=birdy_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    for album in albums:
        return(album['name'])


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

    # # check contents of input track
    # for item in input_track:
    #     print(item)

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

    input_track = request.get_json()

    # get the artist uri and track id
    artist_uri = input_track['artists'][0]['uri']
    track_id = input_track['id']
    
    # use built-in recommendations method to get a list of recommended track objects
    recommendations = sp.recommendations(seed_artist=[artist_uri], 
        seed_tracks=[track_id])['tracks']

    return jsonify(recommendations)