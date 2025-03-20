import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")
#! https://api.spotify.com/v1/me/player/currently-playing

scope = 'user-read-recently-played'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))

def clean_list(list):
    s = ', '.join([item['name'] for item in list])
    return s

def get_recently_played():
    try:
        results = sp.current_user_recently_played(limit=3)
        if results['items']:
            tracks = []
            for item in results['items']:
                track = item['track']
                track_info = {
                    'name' : track['name'],
                    'artists' : clean_list(track['artists']),
                    'link' : track['external_urls']['spotify'],
                    'album_image' : track['album']['images'][0]['url']
                }
                tracks.append(track_info)
            print(tracks)
            return tracks
        else:
            print("No recently played tracks found.")
            return []
    except Exception as e:
        print(f"Error fetching recently played tracks: {e}")
        return [] 

def write_to_file(tracks):
    try:
        if tracks == []: return

        with open('../../recent_tracks.json', 'w') as f:
            json.dump(tracks, f)
            print("File written successfully")
    except Exception as e:
        print(f"Error replacing file: {e}")

t = get_recently_played()
write_to_file(t)