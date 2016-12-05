import networkx as nx
import math
import copy
import time
import xlwt
import scipy.stats
import numpy as np
import csv
from multiprocessing import Process, Value, Array
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures

class GraphMethod:

    G = {}
    nodes_data = {}

    @classmethod
    def __init__(cls):
        print 'Init GraphMethod'

    @staticmethod
    def dijkstra_weight(G):
        sum_all_paths = 0
        for x in G.node:
            sum_all_paths += GraphMethod._calculate_paths_sum(nx.single_source_dijkstra_path_length(G, x))
        return sum_all_paths

    @staticmethod
    def dijkstra_entropy(G):
        sum_all_paths = 0
        for x in G.node:
            sum_all_paths += GraphMethod._calculate_paths_sum(nx.single_source_dijkstra_path_length(G, x, weight='entropy_sum'))
        return sum_all_paths

    @staticmethod
    def find_shortest_path(G):
        entropy_sum = 0
        for x in G.node:
            paths = nx.single_source_dijkstra_path(G, x)
            for path in paths:
                path_nodes = []
                for node in paths[path]:
                    path_nodes.append(G.node[node]['popularity'])
                entropy = scipy.stats.entropy(np.asarray(path_nodes, dtype=float))
                for node in paths[path]:
                    if 'entropy_sum' not in G.node[node]:
                        G.node[node]['entropy_sum'] = entropy
                    else:
                        G.node[node]['entropy_sum'] += entropy
                    if 'betweeness' not in G.node[node]:
                        G.node[node]['betweeness'] = 1
                    else:
                        G.node[node]['betweeness'] += 1

        for x in G.node:
            entropy_sum += G.node[x]['entropy_sum']

        return entropy_sum

    @staticmethod
    def set_edges_weight(G, entropy_sum):
        for i in G.edges():
            entropy_0 = G.node[i[0]]['entropy_sum']
            entropy_1 = G.node[i[1]]['entropy_sum']
            edge_entropy = (entropy_0 + entropy_1)/entropy_sum
            weight_in_min = G.edge[i[0]][i[1]]['weight']/(1-edge_entropy)
            G.edge[i[0]][i[1]]['weight'] = weight_in_min

    @staticmethod
    def _calculate_paths_sum(tab):
        paths_sum = 0
        for i in tab:
            paths_sum += tab[i]
        return paths_sum

    @staticmethod
    def depth_first_search(G, nodes_data):
        start_time = time.time()
        GraphMethod.G = G
        GraphMethod.nodes_data = nodes_data
        with open('results_with_entropy.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Node_1', 'Node_2', 'Entropy_sum'])

            nodes = G.node

            with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
                for node in nodes:
                    executor.submit(calculate, node, GraphMethod.G, GraphMethod.nodes_data)

            print("--- %s seconds ---" % (time.time() - start_time))


    @staticmethod
    def get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2):
        r = 6371
        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
                                                  math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = r * c
        return math.ceil(d*1000)/1000

    @staticmethod
    def calculate_edge_length(node_1, node_2, nodes_data):
        lat1 = nodes_data[str(node_1)][0]
        lon1 = nodes_data[str(node_1)][1]
        lat2 = nodes_data[str(node_2)][0]
        lon2 = nodes_data[str(node_2)][1]

        distance = GraphMethod.get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2)
        return distance


def calculate(i, G, nodes_data):
    with open('results_with_entropy.csv', 'ab') as csvfile:
        writer = csv.writer(csvfile)
        for j in G.node:
            if j not in G.neighbors(i):
                G_temp = copy.deepcopy(G)
                dist = GraphMethod.calculate_edge_length(i, j, nodes_data)
                G_temp.add_edge(i, j, weight=dist)
                G_temp.add_edge(j, i, weight=dist)
                entropy_sum = GraphMethod.find_shortest_path(G_temp)
                GraphMethod.set_edges_weight(G_temp, entropy_sum)
                new_network_sum = GraphMethod.dijkstra_weight(G_temp)
                print new_network_sum

                writer.writerow([i, j, new_network_sum])

                if new_network_sum < shortest:
                    shortest = new_network_sum

