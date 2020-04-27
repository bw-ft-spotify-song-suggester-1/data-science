# web_app/routes/home_routes.py

from flask import Blueprint, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
from flask_app.services.spotify_service import spotify_api_client

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
def index():
    x = 2 + 2
    return f"The party starts here on {x}"


@home_routes.route("/albums")
def birdy_albums():
    sp = spotify_api_client()
    track = []
    tracky_uri = 'spotify:track:6MjiVEJy1YVuJNFu72OH61'
    track.append(tracky_uri)
    results = sp.audio_features(tracks=track)
    return results
    #  sp = spotify_api_client()
    # birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
    # results = sp.artist(artist_id=birdy_uri)
    # return results
    # results = sp.artist_albums(artist_id=birdy_uri, album_type='album')
    # albums = results['items']
    # while results['next']:
    #     results = spotify.next(results)
    #     albums.extend(results['items'])

    # for album in albums:
    #     return(album['name'])

