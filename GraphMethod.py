import networkx as nx
import math
import copy
import time
import scipy.stats
import numpy as np
import csv
import concurrent.futures
import multiprocessing


class GraphMethod:

    test = 0

    @classmethod
    def __init__(cls):
        print 'Init GraphMethod'

    @classmethod
    def dijkstra_weight(cls, graph):
        sum_all_paths = 0
        for x in graph.node:
            sum_all_paths += cls._calculate_paths_sum(nx.single_source_dijkstra_path_length(graph, x))
        return sum_all_paths

    @classmethod
    def dijkstra_entropy(cls, graph):
        sum_all_paths = 0
        for x in graph.node:
            sum_all_paths += cls._calculate_paths_sum(nx.single_source_dijkstra_path_length(graph, x, weight='entropy_sum'))
        return sum_all_paths

    @classmethod
    def find_shortest_path(cls, graph):
        entropy_sum = 0
        for x in graph.node:
            paths = nx.single_source_dijkstra_path(graph, x)
            for path in paths:
                path_nodes = []
                for node in paths[path]:
                    path_nodes.append(graph.node[node]['popularity'])
                entropy = scipy.stats.entropy(np.asarray(path_nodes, dtype=float))
                for node in paths[path]:
                    if 'entropy_sum' not in graph.node[node]:
                        graph.node[node]['entropy_sum'] = entropy
                    else:
                        graph.node[node]['entropy_sum'] += entropy
                    if 'betweeness' not in graph.node[node]:
                        graph.node[node]['betweeness'] = 1
                    else:
                        graph.node[node]['betweeness'] += 1

        for x in graph.node:
            entropy_sum += graph.node[x]['entropy_sum']

        return entropy_sum

    @classmethod
    def set_edges_weight(cls, graph, entropy_sum):
        for i in graph.edges():
            entropy_0 = graph.node[i[0]]['entropy_sum']
            entropy_1 = graph.node[i[1]]['entropy_sum']
            edge_entropy = (entropy_0 + entropy_1)/entropy_sum
            weight_in_min = graph.edge[i[0]][i[1]]['weight']/(1-edge_entropy)
            graph.edge[i[0]][i[1]]['weight'] = weight_in_min

    @classmethod
    def _calculate_paths_sum(cls, tab):
        paths_sum = 0
        for i in tab:
            paths_sum += tab[i]
        return paths_sum

    @classmethod
    def depth_first_search(cls, graph, nodes_data):
        start_time = time.time()
        manager = multiprocessing.Manager()
        q = manager.Queue()
        nodes = graph.node

        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            future_to_file = dict((executor.submit(calculate, node, graph, nodes_data, cls, q), node) for node in nodes)
            for future in concurrent.futures.as_completed(future_to_file):
                f = future_to_file[future]
                if future.exception() is not None:
                    print('%r generated an exception: %s' % (f, future.exception()))

            with open('results_with_entropy.csv', 'wb') as csvfile:
                print "Zapis do pliku"
                writer = csv.writer(csvfile)
                writer.writerow(['Node_1', 'Node_2', 'Entropy_sum'])
                while not q.empty():
                    writer.writerow(q.get())

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

    @classmethod
    def compute_edge_weight(cls, graph):
        start_node = 0
        for node in graph.node:
            if graph.node[node]['popularity'] == 1:
                start_node = node
                break

        cls.bfs(graph, start_node, 1)
        cls.bfs(graph, start_node, 2)

    @classmethod
    def bfs(cls, graph, start_node, action):
        visited = [False] * 368
        manager = multiprocessing.Manager()
        queue = manager.Queue()
        queue.put(int(start_node))
        visited[int(start_node)] = True

        while queue.qsize() != 0:
            v = queue.get()
            if action == 1:
                cls.compute_weight_for_edge(v, graph)
            else:
                cls.check_weight(v, graph)

            for neighbor in graph.neighbors(str(v)):
                if not visited[int(neighbor)]:
                    queue.put(int(neighbor))
                    visited[int(neighbor)] = True

    @classmethod
    def compute_weight_for_edge(cls, current_node, graph):
        neighbors = graph.neighbors(str(current_node))
        init_weight = graph.node[str(current_node)]['entry']/len(neighbors)
        for neighbor in neighbors:
            graph.edge[str(current_node)][neighbor]['travelers'] = float("{0:.2f}".format(init_weight))

    @classmethod
    def check_weight(cls, current_node, graph):
        travelers = 0
        i = 0
        for edge in graph.edge:
            if str(current_node) in graph.edge[edge]:
                travelers += graph.edge[edge][str(current_node)]['travelers']
                graph.edge[edge][str(current_node)]['weight'] = \
                    float("{0:.2f}".format(
                    graph.edge[edge][str(current_node)]['travelers'] * \
                    graph.edge[edge][str(current_node)]['travel_time']))
                i += 1

        if travelers > graph.node[str(current_node)]['exit']:
            print "--- no: {0:3d}, " \
                  "node: {1:3d},  " \
                  "travelers: {2:6.3f}, " \
                  "max_exit: {3:6.3f}, " \
                  "edges: {4:1d} ---"\
                .format(cls.test, current_node, travelers, graph.node[str(current_node)]['exit'], i)

            cls.test += 1



def calculate(i, graph, nodes_data, graphmethod, q):

    for j in graph.node:
        if j not in graph.neighbors(i):
            G_temp = copy.deepcopy(graph)
            dist = graphmethod.calculate_edge_length(i, j, nodes_data)
            G_temp.add_edge(i, j, weight=dist)
            G_temp.add_edge(j, i, weight=dist)
            entropy_sum = graphmethod.find_shortest_path(G_temp)
            graphmethod.set_edges_weight(G_temp, entropy_sum)
            new_network_sum = graphmethod.dijkstra_weight(G_temp)
            #print [i, j, new_network_sum]
            result = (i, j, new_network_sum)
            q.put(result)
            print 90506 - q.qsize()
