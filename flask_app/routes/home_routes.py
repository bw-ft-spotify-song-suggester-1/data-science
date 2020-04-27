# web_app/routes/home_routes.py

from flask import Blueprint, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
from flask_app.services.spotify_service import spotify_api_client

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
def index():
    x = 2 + 2
    return f"The party starts here on {x}"

@home_routes.route("/artist")
def artist_profile():
    sp = spotify_api_client()
    artist_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
    results = sp.artist(artist_id=artist_uri)
    return results

@home_routes.route("/audio-features")
def audio_feat():
    sp = spotify_api_client()
    tracky_uri = 'spotify:track:6MjiVEJy1YVuJNFu72OH61'
    results = sp.audio_features(tracks=tracky_uri)
    for r in results:
        return jsonify(r)

@home_routes.route("/album-list")
def album_list():
    sp = spotify_api_client()
    birdy_uri ='spotify:artist:2WX2uTcsvV5OnS0inACecP'
    results = sp.artist_albums(artist_id=birdy_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    for album in albums:
        return(album['name'])