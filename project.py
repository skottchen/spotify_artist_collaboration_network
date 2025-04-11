import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import randomcolor as rc
import csv
from fetch_api_data import fetch_api_data
from clean_json_files import clean_json_files

fig = plt.figure()

def get_top_artists_with_colabs():
    """
    Extracts a list of artist names from the cleaned Spotify collaboration data.

    Returns:
        list: A list of artist names who have at least one collaboration.
    """
    top_artists = []
    with open("Spotify_API_data/cleaned_artists_colab_data.json", "r") as file:
        data = json.load(file)
        for artist_elem in data:
            top_artists.append(artist_elem["artist_name"])
    return top_artists


def generate_random_colors():
    """
    Generates a list of 61 unique random colors for coloring graph nodes.

    Returns:
        list: A list of 61 hex color codes.
    """
    color_map = []
    init_color = rc.RandomColor()
    for _ in range(0, 61):
        rand_color = init_color.generate(luminosity='dark')[0]

        # ensure each node in the graph has a different color
        while rand_color in color_map:
            rand_color = init_color.generate(luminosity='random')[0]

        color_map.append(rand_color)
    return color_map


def generate_graph():
    """
    Constructs a NetworkX graph from cleaned Spotify collaboration data,
    where each node represents an artist and each edge represents a collaboration.
    Also saves a PNG image of the graph.

    Returns:
        tuple: A tuple containing:
            - G (networkx.Graph): The generated graph object.
            - artist_num_colabs (dict): A dictionary mapping each artist to their total number of collaborations.
    """
    G = nx.Graph()
    with open("Spotify_API_data/cleaned_artists_colab_data.json", 'r') as file:
        data = json.load(file)
        node_sizes = []
        artist_num_colabs = {}
        top_artists = get_top_artists_with_colabs()
        for artist_elem in data:
            artist_node_size = 0
            for key, artist in artist_elem.items():
                if key == "artist_name":
                    G.add_node(artist)

                if key == "artist_collaborations":
                    for colab_artist, num_colabs in artist_elem["artist_collaborations"].items():
                        # only add edge if colab_artist is in cleaned_artists_data.json
                        # this ensures that the number of nodes in the graph are the same as the number of artists in cleaned_artists_data.json
                        if colab_artist in top_artists:
                            G.add_edge(
                                artist_elem["artist_name"], colab_artist)
                            artist_node_size += num_colabs

            node_sizes.append(artist_node_size * 50)
            artist_num_colabs[artist_elem["artist_name"]] = artist_node_size

        pos = nx.spring_layout(G, k=3/(np.sqrt(len(G.nodes()))), seed=30)
        color_map = generate_random_colors()
        nx.draw(G, pos, node_size=node_sizes,
                node_color=color_map, edge_color='red')
        nx.draw_networkx_labels(G, pos, font_size=12,
                                font_color='white', font_weight='bold')
        # change background color of graph to black
        fig.set_facecolor("#00000F")

        plt.savefig("Outputs/artists_collaboration_graph.png")
        return G, artist_num_colabs


def write_graph_data_to_csv(degree_centrality, artist_num_colabs):
    """
    Writes network analysis results, including degree centrality and number of collaborations, to a CSV file.

    Args:
        degree_centrality (dict): Dictionary of degree centrality values for each artist.
        artist_num_colabs (dict): Dictionary of the number of collaborations per artist.
    """
    # combine 2 dictionaries
    combined_dict = {}
    for artist in artist_num_colabs:
        combined_dict[artist] = (
            round(degree_centrality[artist], 2), artist_num_colabs[artist])

    combined_dict = dict(sorted(combined_dict.items(),
                                key=lambda item: item[1], reverse=True))

    # write combined_dict to CSV file
    with open("Outputs/network_analysis_results.csv", "w", newline='') as file:
        fieldnames = ["Artist", "Degree Centrality", "Number of Collaborations"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in combined_dict.items():
            writer.writerow({"Artist": key, "Degree Centrality": value[0], "Number of Collaborations": value[1]})\
                
def perform_network_analysis():  
    """
    Executes the network analysis pipeline:
    - Generates a graph from cleaned data
    - Computes degree centrality
    - Writes results to a CSV file
    """
    network_graph, artist_num_colabs = generate_graph()
    degree_centrality = nx.degree_centrality(network_graph)
    write_graph_data_to_csv(degree_centrality, artist_num_colabs)

def main():
    """
    Entry point for the script. Executes the full data pipeline:
    - Fetches Spotify API data
    - Cleans the raw data
    - Performs network analysis and saves outputs
    """
    fetch_api_data()
    clean_json_files()
    perform_network_analysis()
    print("Finish network analysis of top Spotify artists")
    
if __name__ == "__main__":
    main()
