# web_app/routes/home_routes.py

from flask import Blueprint, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
from flask_app.services.spotify_service import spotify_api_client
import gunicorn
import psycopg2
import pandas as pd
from joblib import dump, load
from sklearn import preprocessing

home_routes = Blueprint("home_routes", __name__)


@home_routes.route("/")
def index():
    return "Welcome to our Spotify Song Suggester!"


@home_routes.route("/recommendations/json", methods=['POST'])
def recs_from_basic_json():
    """
    Takes in a JSON string containing track name and artist name from a
    POST request and returns a list of recommended tracks as a JSON object
    using an ML Model.
    """

    sp = spotify_api_client()

    # Check if we got a json object. If we do, assign it to "input_track".
    if not request.json:
        return jsonify({"error": "no request received"})

    input_track = request.get_json(force=True)

    artist = input_track['artist'].lower()
    name = input_track['name'].lower()

    # Query spotify for tracks that match artist and track
    # https://developer.spotify.com/documentation/web-api/reference/search/search/
    search_results = sp.search(q='artist:' + artist + ' track:' + name,
                               type='track', limit=10)
    search_results = search_results['tracks']['items']

    # Now we need to check for exact matches
    # This removes "Live" and "Concert" versions
    # Multiple tracks in the list indicates a track was on multiple albums
    matches = []
    for track in search_results:

        # Get the track name, artist, album, uri, and id
        track_info = get_basic_track_info(track)

        # Get lowercase versions of track name and artist name
        track_name = track_info["name"].lower()
        artist_name = track_info["artist"].lower()

        if name == track_name and artist == artist_name:
            matches.append(track_info)

        else:
            pass

    # If we have no exact matches check to see if the spotify query returned
    # any results. If yes, use the first query result. Else, return an error
    if len(matches) == 0:

        if len(search_results) != 0:
            model_input_track = get_basic_track_info(search_results[0])

        else:
            return jsonify({"error": "track not found."})

    # Else, use the first match to make recommendations
    else:
        model_input_track = matches[0]

    # Get the track features needed for the ML model
    input_df = get_features(model_input_track)

    # Get recommendations. Will be a list of JSON track objects.
    recommendations = get_recommendations(input_df, model_input_track['uri'])

    return jsonify(recommendations)


@home_routes.route("/recommendations/json/full", methods=['POST'])
def recs_from_full_json():
    """
    Takes in a spotify track JSON object from a POST request and returns a
    list of recommended tracks as a JSON object using an ML Model.
    Can also take a JSON string containing id and uri.
    """

    sp = spotify_api_client()

    # Check if we got a json object. If we do, assign it to "input_track"
    if not request.json:
        return jsonify({"error": "no request received"})

    input_track = request.get_json(force=True)

    # Get the track features needed for the ML model
    input_df = get_features(input_track)

    # Get recommendations. Will be a list of JSON track objects.
    recommendations = get_recommendations(input_df, input_track['uri'])

    return jsonify(recommendations)


@home_routes.route("/recommendations/builtin/json", methods=['POST'])
def recs_from_json_builtin():
    """
    Takes in a spotify track object from a POST request and returns a
    list of recommended tracks as a JSON object using the built-in spotify
    recommendations method.
    """
    sp = spotify_api_client()

    if not request.json:
        return jsonify({"error": "no request received"})

    input_track = request.get_json(force=True)

    # get the artist uri and track id
    artist_uri = input_track['artists'][0]['uri']
    track_id = input_track['id']

    # use built-in recommendation method to get a list of recommended tracks
    recommendations = sp.recommendations(seed_artist=[artist_uri],
                                         seed_tracks=[track_id])['tracks']

    return jsonify(recommendations)


@home_routes.route("/full_track/<id>")
def full_track(id):
    """Get spotify track JSON object for a given track id"""
    sp = spotify_api_client()
    track = sp.track(id)

    return track


@home_routes.route("/basic_track/<id>")
def basic_track(id):
    """Get dictionary of basic track info for a given track id"""
    sp = spotify_api_client()
    track = sp.track(id)

    return get_basic_track_info(track)


def get_features(input_track):
    """
    Takes a JSON object or JSON string containing a track id, and returns a
    dataframe containing the features used in the ML model.
    """

    sp = spotify_api_client()

    track_id = input_track['id']

    # get the audio analysis and audio features for the track
    audio_analysis = sp.audio_analysis(track_id)
    audio_features = sp.audio_features(track_id)[0]

    # Get sections and chorus_hit features from the audio analysis
    # sections: # of sections in the song (Verse 1, Chorus 1, Bridge, etc.)
    # chorus_hit: when the first chorus starts (second mark in track)
    sections = len(audio_analysis['sections'])
    chorus_hit = audio_analysis['sections'][2]['start']

    # Create dictionary containing only the necessary features from audio feat
    keys = ["danceability", "energy", "key", "loudness", "mode", "speechiness",
            "acousticness", "instrumentalness", "liveness", "valence", "tempo",
            "duration_ms", "time_signature"]
    features = {key: audio_features[key] for key in keys}

    # add the audio analysis features to the dictionary
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

    # Combine dataframes
    frames = [dataset60, dataset70, dataset80, dataset90, dataset00, dataset10]
    spotify_songs_df = pd.concat(frames, ignore_index=True)

    # Drop the target column and drop duplicates
    spotify_songs_df = spotify_songs_df.drop(['target'], axis=1)
    spotify_songs_df = spotify_songs_df.drop_duplicates("uri")

    # Create new dataframe with only the uri column
    # Will be used to find the song uri for a given index
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

    # Standardize (z-scores) our input values before inputting into model:
    input_values_only = scaler.transform([input_values_only])

    # Load our ML model from compressed joblib file:
    model_knn = load('model.joblib')

    # Get recommended songs from our model:
    # Output_uris is a list containing the index for each recommended song
    # inside the database
    # Model returns 6 tracks in case 1 is the same as the input track
    output_values, output_uris = model_knn.kneighbors(input_values_only)
    output_values = output_values[0]
    output_uris = output_uris[0]

    # List of Spotify URIs for the songs our model recommended
    # Checks if any recommended track is the same as the input track
    recs_uris = []
    for uri_index in output_uris:
        song_uri = spotify_songs_df_uris[uri_index]

        if song_uri == track_uri:
            pass

        else:
            recs_uris.append(song_uri)

    # Remove extra track if it exists
    max_recs = 5
    if len(recs_uris) > max_recs:
        recs_uris.pop(-1)

    # Get JSON of the full Spotify API "track objects" for the songs
    recs = sp.tracks(recs_uris)["tracks"]

    # Filter the results to have only relevant information for each track.
    filtered_recs = []
    for track in recs:
        filtered_recs.append(get_output_values(track))

    return filtered_recs


def get_output_values(track):
    """
    Given a track object, return a dictionary containing only the desired
    output information to send to front end.
    """
    name = track["name"]
    uri = track["uri"]
    artist = track['artists'][0]['name']
    album = track['album']['name']
    spotify_id = track['id']
    popularity = track['popularity']
    preview_url = track['preview_url']
    image = track['album']['images']

    output = {"name": name, "uri": uri, "artist": artist, "album": album,
              "spotify_id": spotify_id, "popularity": popularity,
              "preview_url": preview_url, "image": image}

    return output


def get_basic_track_info(track):
    """
    Given a track object, return a dictionary of track name, artist name,
    album name, track uri, and track id.
    """
    # Remember that artist and album artist have different entries in the
    # spotify track object.

    name = track["name"]
    artist = track['artists'][0]['name']
    album = track['album']['name']
    uri = track["uri"]
    track_id = track['id']

    output = {"name": name, "artist": artist, "album": album, "uri": uri,
              "id": track_id}

    return output


def print_track_object(track):
    """
    Given a track object, print its contents in a more readable format.
    Trouble shooting function. Does not return anything.
    """

    for key in track:

        if key == "available_markets":
            pass
        else:
            print("\nKEY:", key)

            if isinstance(track[key], dict) is True:
                for subkey in track[key]:
                    print("\tSUBKEY", subkey, "\t", track[key][subkey])

            elif isinstance(track[key], list) is True:
                for item in track[key]:
                    print("\tLIST_ITEM:\t", item)

            else:
                print("\tENTRY:", track[key])
