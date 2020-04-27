import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

CID = os.getenv("Client_ID")
SECRET = os.getenv("Client_Secret")

def spotify_api_client():
    client_credentials_manager = SpotifyClientCredentials(client_id=CID, client_secret=SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp


if __name__ == "__main__":
    sp = spotify_api_client()
    
    
    