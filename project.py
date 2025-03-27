from auth import get_token, get_auth_header
from requests import get
import json
import os
from dotenv import load_dotenv
from collections import OrderedDict
from datetime import datetime

def get_top_artists(token, playlist_id):
    """
    returns a dictionary containing the Spotify ids (keys)
    and artists' names (values) from the Top Artists of 2024 Global playlist
    """
    top_artists = {}
    query_url = f"https://api.spotify.com/v1/playlists/{playlist_id}?market=US&fields=tracks.items%28track%28artists%28id%2C+name%29"
    headers = get_auth_header(token)
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    for track in json_result["tracks"]["items"]:
        artist_lst = track["track"]["artists"]
        for artist in artist_lst:
            if artist['name'] != "¥$":  # pseudonym for Kanye West, who is already in the top artists list
                top_artists[artist['id']] = artist['name']
    top_artists_lst = list(top_artists.items())
    return dict(top_artists_lst)


def get_artist_albums(token, artist_id):
    """
    returns a sorted dictionary with keys being album_id and values being album names 
    (In other words, albums by the artist which artist_id belongs to)
    """
    artist_albums = {}
    query_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?market=US"
    headers = get_auth_header(token)
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    for album in json_result["items"]:
        artist_albums[album["id"]] = (album["name"], album["release_date"])
    return OrderedDict(sorted(artist_albums.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True))


def get_artist_collaborations(token, album_id, album_artist, artist_collaborations, top_artists):
    """
    updates the artist_collaborations dictionary with collaboration info from individual tracks in an album
    """
    # get the tracks associated with the album_id
    # for each track in the album, look through "artists" in items
    # if there's only one artist (themselves), skip that track
    # if there's 2 or more artists
    # check if the artist_id that did the colab is in top_artists
    # if not, create a new entry in the artist_collaborations dictionary
    query_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?market=US"
    headers = get_auth_header(token)
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    for track in json_result["items"]:
        artists_lst = track["artists"]
        if len(artists_lst) >= 2: # skip playlists in which the artist did not collaborate with other artists (common bug)?
            for artist in artists_lst:
                if artist["id"] in top_artists and artist["name"] != album_artist: # check for collaborations with other top artists only
                    artist_name = top_artists.get(artist["id"])
                    if artist["name"] not in artist_collaborations:
                        artist_collaborations[artist_name] = 1
                    else:
                        artist_collaborations[artist_name] += 1
    return artist_collaborations
    

def main():
    token = get_token()
    playlist_id = os.getenv("PLAYLIST_ID")
    collaboration_data = []
    top_artists = get_top_artists(token, playlist_id)
    # setting x and y prevents getting rate limited by API before all data is collected
    x = 61  # inclusive index 
    y = 69  # non_inclusive index
    with open("top_artists.json", "w") as file:
        json.dump(top_artists, file, indent=2)
    for artist_id in list(top_artists.keys())[x:y]:
        artist_colab_dict = {}
        artist_colab_dict["artist_id"] = artist_id
        artist_colab_dict["artist_name"] = top_artists.get(artist_id)
        artist_collaborations = {}
        artist_albums = get_artist_albums(token, artist_id)

        latest_albums = OrderedDict()
        for album_id, (album_name, release_date) in artist_albums.items():
            # CLEANING DATA: Remove version details like "(Taylor's Version)", "(Deluxe Edition)"
            # Prevents getting data from songs that are the same
            base_name = album_name.split(" (")[0]
            if base_name not in latest_albums:
                latest_albums[base_name] = (album_id, album_name, release_date)
                
        # CLEANING DATA in api results for album
        # From the sorted dict if the base_name starts with the same base_name as the next element
            # if the date is less than the date of the previous element
            # remove it from the dictionary
        temp_lst = list(latest_albums.items())
        for i in range(0, len(temp_lst) - 1):
            base_name_1 = temp_lst[i][0]
            base_name_2 = temp_lst[i + 1][0]
            date_1 = temp_lst[i][1][2]
            date_2 = temp_lst[i+1][1][2]
            
            try:
                release_date1 = datetime.strptime(date_1, "%Y-%m-%d")
            except ValueError:
                release_date1 = datetime.strptime(date_1, "%Y")
                
            try:
                release_date2 = datetime.strptime(date_2, "%Y-%m-%d")
            except ValueError:
                release_date2 = datetime.strptime(date_2, "%Y")
                
            if base_name_1.startswith(base_name_2):
                if release_date1 > release_date2: # base_name 1 is the later version
                    latest_albums.pop(base_name_2)
                elif release_date1 < release_date2:  # base_name 2 is the later version
                    latest_albums.pop(base_name_1)
                else:
                    continue
            else:
                continue
        
        for (album_id, name, release_date) in latest_albums.values():
            album_artist = top_artists.get(artist_id)

            # ensure artist_collaborations dict contains information on artist's collaborations across all tracks
            artist_colab_dict["artist_collaborations"] = get_artist_collaborations(
                token, album_id, album_artist, artist_collaborations, top_artists)
        collaboration_data.append(artist_colab_dict) # appends a new entry to the list
        
        # generate data for 10 artists at a time to avoid being rate limited by Spotify API
        with open(f"./Spotify_API_data/artists_{x}_to_{y}.json", "w") as file: 
            json.dump(collaboration_data, file, indent=2)
 
    print("Finished writing data to files.")


if __name__ == "__main__":
    main()