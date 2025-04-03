import json

# combine the Spotify API data files into 1 json file
def process_files(x, y):
    collaborations = []
    BEYONCE_MISSPELLED = "Beyonc\u00e9"
    for _ in range(0, 7):
        with open(f"./Spotify_API_data/artists_{x}_to_{y}.json", "r") as file:
            data = json.load(file)
            for item in data:
                if item["artist_name"] == BEYONCE_MISSPELLED:
                    item["artist_name"] = "Beyonce"
                if item["artist_collaborations"]:  # Remove artists in playlist who had no collaborations
                    for key in item["artist_collaborations"].copy():
                        if key == BEYONCE_MISSPELLED:
                            item["artist_collaborations"]["Beyonce"] = item["artist_collaborations"].get(
                                BEYONCE_MISSPELLED)
                            item["artist_collaborations"].pop(
                                BEYONCE_MISSPELLED)
                    collaborations.append(item)

            if x == 0:
                x += 11
            else:
                x += 10
                
            if y == 61:
                y += 8
            else:
                y += 10

    return collaborations


def main():
    x, y = 0, 11
    collaborations = process_files(x, y)
    # 61 artists in collaborations
    with open("cleaned_artists_data.json", "w") as file:
        json.dump(collaborations, file, indent=2)


main()
