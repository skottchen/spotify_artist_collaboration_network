import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
G = nx.Graph()

with open("cleaned_artists_data.json", 'r') as file:
    data = json.load(file)
    node_sizes = []
    artists = []
    count = 0
    for artist_elem in data:
        artists.append(artist_elem["artist_name"])
        artist_node_size = 0
        for key, artist in artist_elem.items():
            if key == "artist_name":
                G.add_node(artist)

            if key == "artist_collaborations":
                for colab_artist, num_colabs in artist_elem["artist_collaborations"].items():
                    # only add edge if colab_artist is in top_artists.json
                    G.add_edge(artist_elem["artist_name"], colab_artist)
                    artist_node_size += num_colabs
        node_sizes.append(artist_node_size * 100)
    # print(node_sizes)
    # print(len(node_sizes))
    # print(G.number_of_nodes())
    # using seed displays the node in the same position every time the graph is drawn
    pos = nx.spring_layout(G, k=3/(np.sqrt(len(G.nodes()))), seed=38)
    nx.draw(G, pos, with_labels=True)
    # print(artists)
    # print(len(artists))
    # print(list(G.nodes()))
    # print(G.number_of_nodes())
    plt.savefig("Outputs/collaboration_graph.png")
