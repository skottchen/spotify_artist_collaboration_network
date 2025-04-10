import json


def clean_json_files():
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
