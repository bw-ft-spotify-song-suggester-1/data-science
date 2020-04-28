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


# sample id: 6rqhFgbbKwnb9MLmUQDhG6
@home_routes.route("/recommendations/<id>")
def recs_from_id(id):
    sp = spotify_api_client()

    # get the track object based on the input id
    input_track = sp.track(id)

    # get artist uri from the track object
    artist_uri = input_track['artists'][0]['uri']

    # # check contents of input track
    # for item in input_track:
    #     print(item)

    recommendations = sp.recommendations(seed_artist=[artist_uri], seed_tracks=[id])['tracks']

    # # Enable code to print list of recommended tracks
    # print('\ntracks')
    # i=1
    # for item in recommendations['tracks']:
    #     print(i, item, '\n')
    #     i+=1


    return recommendations

@home_routes.route("/recommendations", methods=['POST'])
def builtin_recs_blah():
    
    sp = spotify_api_client()
    #input_track = sp.track(id)

    input_track = request.get_json()

    """
    print("\n\n")
    for item in input_track:
        print(item)
    print("\n\n")
    """

    # use this to see list of valid genres
    #sp.recommendation_genre_seeds()

    
    #print('\n',input_track['artists'][0]['uri'], '\n')
    artist_uri = input_track['artists'][0]['uri']
    track_id = input_track['id']
    
    recommendations = sp.recommendations(seed_artist=[artist_uri], seed_tracks=[track_id])
    # i=1
    # for item in recommendations:
    #     print(i, item)
    #     i+=1
    
    print('\ntracks')
    i=1
    for item in recommendations['tracks']:
        print(i, item, '\n')
        i+=1

    # print("\nSeeds")
    # i=1
    # for item in recommendations['seeds']:
    #     print(i, item)
    #     i+=1

    return recommendations