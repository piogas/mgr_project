import networkx as nx
import math
import copy
import time
import scipy.stats
import numpy as np
import csv
import concurrent.futures
from Queue import Queue

class GraphMethod:


    results = Queue()

    @classmethod
    def __init__(cls):
        print 'Init GraphMethod'

    @classmethod
    def dijkstra_weight(cls, G):
        sum_all_paths = 0
        for x in G.node:
            sum_all_paths += cls._calculate_paths_sum(nx.single_source_dijkstra_path_length(G, x))
        return sum_all_paths

    @classmethod
    def dijkstra_entropy(cls, G):
        sum_all_paths = 0
        for x in G.node:
            sum_all_paths += cls._calculate_paths_sum(nx.single_source_dijkstra_path_length(G, x, weight='entropy_sum'))
        return sum_all_paths

    @classmethod
    def find_shortest_path(cls, G):
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

    @classmethod
    def set_edges_weight(cls, G, entropy_sum):
        for i in G.edges():
            entropy_0 = G.node[i[0]]['entropy_sum']
            entropy_1 = G.node[i[1]]['entropy_sum']
            edge_entropy = (entropy_0 + entropy_1)/entropy_sum
            weight_in_min = G.edge[i[0]][i[1]]['weight']/(1-edge_entropy)
            G.edge[i[0]][i[1]]['weight'] = weight_in_min

    @classmethod
    def _calculate_paths_sum(cls, tab):
        paths_sum = 0
        for i in tab:
            paths_sum += tab[i]
        return paths_sum

    @classmethod
    def depth_first_search(cls, G, nodes_data):
        start_time = time.time()

        nodes = G.node

        with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
            future_to_file = dict((executor.submit(calculate, node, G, nodes_data, cls), node) for node in nodes)
            for future in concurrent.futures.as_completed(future_to_file):
                f = future_to_file[future]
                if future.exception() is not None:
                    print('%r generated an exception: %s' % (f, future.exception()))
            with open('results_with_entropy.csv', 'wb') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Node_1', 'Node_2', 'Entropy_sum'])
                for result in iter(cls.results.get, None):
                    writer.writerow(result)

            print("--- %s seconds ---" % (time.time() - start_time))

    @classmethod
    def get_distance_from_lat_lon_in_km(cls, lat1, lon1, lat2, lon2):
        r = 6371
        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
                                                  math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = r * c
        return math.ceil(d*1000)/1000

    @classmethod
    def calculate_edge_length(cls, node_1, node_2, nodes_data):
        lat1 = nodes_data[str(node_1)][0]
        lon1 = nodes_data[str(node_1)][1]
        lat2 = nodes_data[str(node_2)][0]
        lon2 = nodes_data[str(node_2)][1]

        distance = cls.get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2)
        return distance


def calculate(i, G, nodes_data, graphmethod):

    for j in G.node:
        if j not in G.neighbors(i):
            G_temp = copy.deepcopy(G)
            dist = graphmethod.calculate_edge_length(i, j, nodes_data)
            G_temp.add_edge(i, j, weight=dist)
            G_temp.add_edge(j, i, weight=dist)
            entropy_sum = graphmethod.find_shortest_path(G_temp)
            graphmethod.set_edges_weight(G_temp, entropy_sum)
            new_network_sum = graphmethod.dijkstra_weight(G_temp)
            print [i, j, new_network_sum]

            graphmethod.results.put([i, j, new_network_sum])

