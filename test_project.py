import json
from project import generate_graph
from clean_json_files import clean_json_files
from auth import get_token, get_auth_header
import json
from dotenv import load_dotenv
from fetch_api_data import spotify_get
load_dotenv()

# test that the graph has the same number of nodes (61) as the number of
# artists with colabs in cleaned_artists_colab_data.json
def test_generate_graph():
    network_graph, _ = generate_graph()
    num_nodes = network_graph.number_of_nodes()
    with open("Spotify_API_data/cleaned_artists_colab_data.json", "r") as file:
        data = json.load(file)
        assert num_nodes == len(data)

# test that none of the "artist_collaborations" dicts in cleaned_artists_colab_data.json
# contain the artist's own name and are not empty (meaning that the artist had no collaborations)
def test_clean_json_files():
    collaborations = clean_json_files()
    for artist in collaborations:
        colab_dict = artist["artist_collaborations"]
        assert len(colab_dict) > 0
        for artist_name in colab_dict:
            assert artist_name != artist["artist_name"]

# test spotify_get returns fetches from the API
def test_spotify_get():
    BASE_URL = "https://api.spotify.com/v1"
    token = get_token()
    headers = get_auth_header(token)
    artist_id = "0Y5tJX1MQlPlqiwlOH1tJY" # random artist_id
    url = f"{BASE_URL}/artists/{artist_id}/albums?market=US"
    data = spotify_get(url, headers)
    assert data is not None
