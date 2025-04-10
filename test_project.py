import json
from project import generate_graph
from clean_json_files import clean_json_files

# check that the graph has the same number of nodes (61) as the number of
# artists with colabs in cleaned_artists_colab_data.json
def test_generate_graph():
    network_graph, _ = generate_graph()
    num_nodes = network_graph.number_of_nodes()
    with open("Spotify_API_data/cleaned_artists_colab_data.json", "r") as file:
        data = json.load(file)
        assert num_nodes == len(data)

# make sure none of the "artist_collaborations" dicts in cleaned_artists_colab_data.json
# contain the artist's own name and are not empty (meaning that the artist had no collaborations)
def test_clean_json_files():
    collaborations = clean_json_files()
    for artist in collaborations:
        colab_dict = artist["artist_collaborations"]
        assert len(colab_dict) > 0
        for artist_name in colab_dict:
            assert artist_name != artist["artist_name"]

