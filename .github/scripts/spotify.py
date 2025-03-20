import spotipy
import json
import os
import base64

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
    with open("recent_tracks.json", "w") as f:
        json.dump(tracks, f, indent=4)

if __name__ == "__main__":
    import requests
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