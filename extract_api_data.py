from auth import get_token, get_auth_header
import requests
import json
import os
from dotenv import load_dotenv
from collections import OrderedDict
from datetime import datetime
import time

load_dotenv()

BASE_URL = "https://api.spotify.com/v1"
session = requests.Session()

def spotify_get(url, headers, max_retries=3):
    for _ in range(max_retries):
        response = session.get(url, headers=headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "10"))
            print(f"Rate limited. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
     
        elif response.status_code >= 500:
            print(
                f"Server error {response.status_code}. Retrying in 5 seconds...")
            time.sleep(5)
          
        elif response.ok:
            return response.json()
        else:
            print(f"Request failed: {response.status_code}, {response.text}")
            break
    return {}


def get_top_artists(token, playlist_id):
    top_artists = {}
    url = f"{BASE_URL}/playlists/{playlist_id}?market=US&fields=tracks.items(track(artists(id,name)))"
    headers = get_auth_header(token)
    data = spotify_get(url, headers)

    for item in data.get("tracks", {}).get("items", []):
        for artist in item["track"]["artists"]:
            if artist["name"] != "¥$":
                top_artists[artist["id"]] = artist["name"]

    return dict(top_artists.items())


def get_artist_albums(token, artist_id):
    albums = {}
    url = f"{BASE_URL}/artists/{artist_id}/albums?market=US"
    headers = get_auth_header(token)
    data = spotify_get(url, headers)

    for album in data.get("items", []):
        albums[album["id"]] = (album["name"], album["release_date"])

    return OrderedDict(sorted(albums.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True))


def get_artist_collaborations(token, album_id, album_artist, artist_collaborations, top_artists):
    url = f"{BASE_URL}/albums/{album_id}/tracks?market=US"
    headers = get_auth_header(token)
    data = spotify_get(url, headers)

    for track in data.get("items", []):
        artists = track["artists"]
        if len(artists) < 2:
            continue
        for artist in artists:
            if artist["id"] in top_artists and artist["name"] != album_artist:
                name = top_artists[artist["id"]]
                artist_collaborations[name] = artist_collaborations.get(
                    name, 0) + 1
    return artist_collaborations


def clean_album_names(albums):
    latest = {}
    for album_id, (name, date) in albums.items():
        base = name.split(" (")[0]
        if base not in latest:
            latest[base] = (album_id, name, date)

    # Remove older versions with the same base name
    temp = list(latest.items())
    i = 0
    while i < len(temp) - 1:
        base1, (_, _, d1) = temp[i]
        base2, (_, _, d2) = temp[i + 1]
        try:
            r1 = datetime.strptime(d1, "%Y-%m-%d")
        except ValueError:
            r1 = datetime.strptime(d1, "%Y")
        try:
            r2 = datetime.strptime(d2, "%Y-%m-%d")
        except ValueError:
            r2 = datetime.strptime(d2, "%Y")
        if base1.startswith(base2):
            if r1 > r2:
                latest.pop(base2)
            else:
                latest.pop(base1)
        i += 1
    return latest


def extract_api_data():
    token = get_token()
    playlist_id = os.getenv("PLAYLIST_ID")
    top_artists = get_top_artists(token, playlist_id)

    with open("Spotify_API_data/top_artists.json", "w") as f:
        json.dump(top_artists, f, indent=2)

    artist_ids = list(top_artists.keys())
    collaboration_data = []

    for i, artist_id in enumerate(artist_ids):
        print(
            f"Processing artist {i+1}/{len(artist_ids)}: {top_artists[artist_id]}")
        artist_colab_dict = {
            "artist_id": artist_id,
            "artist_name": top_artists[artist_id],
            "artist_collaborations": {}
        }

        albums = get_artist_albums(token, artist_id)
        cleaned_albums = clean_album_names(albums)

        for album_id, _, _ in cleaned_albums.values():
            get_artist_collaborations(
                token,
                album_id,
                artist_colab_dict["artist_name"],
                artist_colab_dict["artist_collaborations"],
                top_artists
            )

        collaboration_data.append(artist_colab_dict)

        with open("./Spotify_API_data/artists_colab_data.json", "w") as f:
            json.dump(collaboration_data, f, indent=2)

        time.sleep(1)
    
    print("Finished fetching data from Spotify API")
