import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import randomcolor as rc
fig = plt.figure()

def create_graph_and_csv():
    """
    generates a graph and CSV of the data from the Spotify API
    """
    G = nx.Graph()
    with open("cleaned_artists_data.json", 'r') as file:
        data = json.load(file)
        node_sizes = []
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
                            G.add_edge(artist_elem["artist_name"], colab_artist)
                            artist_node_size += num_colabs
                            
            node_sizes.append(artist_node_size * 50)
        pos = nx.spring_layout(G, k=3/(np.sqrt(len(G.nodes()))), seed = 30)
        color_map = generate_random_colors()
        nx.draw(G, pos, node_size=node_sizes,
                node_color=color_map, edge_color='red')
        nx.draw_networkx_labels(G, pos, font_size=12, font_color='white', font_weight = 'bold')
        fig.set_facecolor("#00000F") # change background color of graph to black
        
        plt.savefig("Outputs/collaboration_graph.png")

def get_top_artists_with_colabs():
    """
    returns a list of artist_names in cleaned_artists_data.json
        - this is all artists who were authors of tracks with collaborations
    """
    top_artists = []
    with open("cleaned_artists_data.json", "r") as file:
        data = json.load(file)
        for artist_elem in data:
            top_artists.append(artist_elem["artist_name"])
    return top_artists

def generate_random_colors():
    """
    returns a color map with 61 random colors - one for each node
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

create_graph_and_csv()
