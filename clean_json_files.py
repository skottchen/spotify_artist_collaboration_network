import json

def clean_json_files():
    collaborations = []
    BEYONCE_MISSPELLED = "Beyonc\u00e9"
    with open("./Spotify_API_data/artists_colab_data.json", "r") as file:
        data = json.load(file)
        for item in data:
            if item["artist_name"] == BEYONCE_MISSPELLED:
                item["artist_name"] = "Beyonce"

            # Remove artists in playlist who had no collaborations
            if item["artist_collaborations"]:
                for key in item["artist_collaborations"].copy():
                    if key == BEYONCE_MISSPELLED:
                        item["artist_collaborations"]["Beyonce"] = item["artist_collaborations"].get(
                            BEYONCE_MISSPELLED)
                        item["artist_collaborations"].pop(
                            BEYONCE_MISSPELLED)
                collaborations.append(item)

    with open("./Spotify_API_data/artists_colab_data.json", "w") as file:
        json.dump(collaborations, file, indent=2)
        
    print("Finished cleaning artists_colab_data.json")