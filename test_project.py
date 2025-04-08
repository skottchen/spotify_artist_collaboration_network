import pytest
import json
from perform_network_analysis import generate_graph
# check that the graph has the same number of nodes (61) as the number of
# artists in artists_colab.json
def test_number_of_nodes():
    network_graph, _ = generate_graph()
    num_nodes = network_graph.number_of_nodes()
    with open("artists_colab.json", "r") as file:
        data = json.load(file)
        print(len(data))
        

test_number_of_nodes()
