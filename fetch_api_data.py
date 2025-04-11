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
    """
    Sends a GET request to the given Spotify API URL with retry handling for rate limits and server errors.

    Args:
        url (str): The full Spotify API endpoint.
        headers (dict): Authorization headers containing the access token.
        max_retries (int): Maximum number of retries for failed requests.

    Returns:
        dict: Parsed JSON response from the API or an empty dictionary on failure.
    """
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
    """
    Retrieves the unique artists from a given Spotify playlist.

    Args:
        token (str): Spotify API access token.
        playlist_id (str): Spotify playlist ID.

    Returns:
        dict: Dictionary mapping artist IDs to artist names.
    """
    top_artists = {}
    url = f"{BASE_URL}/playlists/{playlist_id}?market=US&fields=tracks.items(track(artists(id,name)))"
    headers = get_auth_header(token)
    data = spotify_get(url, headers)

    for item in data.get("tracks", {}).get("items", []):
        for artist in item["track"]["artists"]:
            if artist["name"] != "¥$":
                top_artists[artist["id"]] = artist["name"]

    top_artists["6vWDO969PvNqNYHIOW5v0m"] = "Beyonce"
    return dict(top_artists.items())


def get_artist_albums(token, artist_id):
    """
    Fetches all albums for a given artist and sorts them in descending order
    by album name and release date.

    Args:
        token (str): Spotify API access token.
        artist_id (str): Spotify artist ID.

    Returns:
        OrderedDict: Albums sorted by (name, release_date), in reverse order.
    """
    albums = {}
    url = f"{BASE_URL}/artists/{artist_id}/albums?market=US"
    headers = get_auth_header(token)
    data = spotify_get(url, headers)

    for album in data.get("items", []):
        albums[album["id"]] = (album["name"], album["release_date"])

    return OrderedDict(sorted(albums.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True))


def get_artist_collaborations(token, album_id, album_artist, artist_collaborations, top_artists):
    """
    Updates the artist_collaborations dictionary with collaboration counts
    based on the tracks of a given album.

    Args:
        token (str): Spotify API access token.
        album_id (str): Spotify album ID.
        album_artist (str): Name of the album's main artist.
        artist_collaborations (dict): Dictionary of current collaboration counts.
        top_artists (dict): Dictionary of top artist IDs and names.

    Returns:
        dict: Updated dictionary of collaboration counts.
    """
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
    """
    Cleans album data by keeping only the latest version of each album
    (based on the base name) to avoid duplicates.

    Args:
        albums (dict): Dictionary mapping album IDs to tuples of (name, release_date).

    Returns:
        dict: Dictionary of latest albums with unique base names.
    """
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


def fetch_api_data():
    """
    Main function that coordinates data extraction from Spotify API:
    - Retrieves top artists from a playlist.
    - Saves the top artist data to a JSON file.
    - Retrieves and cleans each artist’s albums.
    - Extracts artist collaborations from album tracks.
    - Saves raw collaboration data to a JSON file.

    Outputs:
        Writes two JSON files to the 'Spotify_API_data/' directory:
            - top_artists.json
            - raw_artists_colab_data.json
    """
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

        with open("./Spotify_API_data/raw_artists_colab_data.json", "w") as f:
            json.dump(collaboration_data, f, indent=2)

        time.sleep(1)

    print("Finished fetching raw data from Spotify API\n")
