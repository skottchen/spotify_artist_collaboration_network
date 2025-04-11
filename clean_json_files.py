import json


def clean_json_files():
    """
    Cleans the raw artist collaboration data retrieved from the Spotify API.

    This function:
    - Loads data from 'raw_artists_colab_data.json'
    - Removes the first listed collaboration for Beyoncé (assumed to be incorrect or unwanted)
    - Excludes any artists that have no recorded collaborations
    - Saves the cleaned data to 'cleaned_artists_colab_data.json'

    Returns:
        list: A list of cleaned artist collaboration records.
    """
    collaborations = []
    with open("./Spotify_API_data/raw_artists_colab_data.json", "r") as file:
        data = json.load(file)
        for item in data:
            if item["artist_name"] == "Beyonce":

                # remove first item from Beyonce artist colab dict
                del item["artist_collaborations"][list(
                    item["artist_collaborations"].keys())[0]]

            # Remove artists in playlist who had no collaborations
            if item["artist_collaborations"]:
                collaborations.append(item)

    with open("./Spotify_API_data/cleaned_artists_colab_data.json", "w") as file:
        json.dump(collaborations, file, indent=2)

    print("Finished cleaning Spotify API data\n")
    return collaborations
