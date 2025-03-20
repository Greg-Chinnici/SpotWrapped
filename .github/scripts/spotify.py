import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
import requests
import base64

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

CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

def get_access_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result.get("access_token")
    return token

def get_recently_played(token):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=3"
    headers = {"Authorization": f"Bearer {token}"}
    result = requests.get(url, headers=headers)
    return json.loads(result.content)

def update_recent_tracks_file(tracks):
    if (tracks == []):
        return
    with open("../../recent_tracks.json", "w") as f:
        json.dump(tracks, f, indent=4)

if __name__ == "__main__":
    access_token = get_access_token()
    recently_played = get_recently_played(access_token)
    tracks = []
    if recently_played and 'items' in recently_played:
        for item in recently_played['items']:
            track = item['track']
            track = {
                "name": track['name'],
                "artists": clean_list(track['artists']),
                "album": item['track']['album']['name'],
                "album_image": track['album']['images'][0]['url'],
                "link": track['external_urls']['spotify'],
            }
            tracks.append(track)
        update_recent_tracks_file(tracks)
    else:
        print("Could not retrieve recently played tracks")
