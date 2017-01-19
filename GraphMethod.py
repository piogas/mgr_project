import networkx as nx
import math
import copy
import time
import scipy.stats
import numpy as np
import csv
import concurrent.futures
import multiprocessing
import utils





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
            sum_all_paths += cls._calculate_paths_sum(nx.single_source_dijkstra_path_length(graph, x,
                                                                                            weight='entropy_sum'))
        return sum_all_paths

    @classmethod
    def find_shortest_path_entropy(cls, graph):
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
                    entropy_sum += entropy

        return entropy_sum

    @classmethod
    def find_shortest_path_travelers(cls, graph):
        travelers_sum = 0
        for x in graph.node:
            paths = nx.single_source_dijkstra_path(graph, x)
            length = nx.single_source_dijkstra_path_length(graph, x)
            for path in paths:
                entry_exits = 0
                for node in paths[path]:
                    entry_exits += graph.node[node]['entry_exit']
                travelers_sum += entry_exits * length[path]
        return travelers_sum
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
    def depth_first_search(cls, graph, nodes_data, poly1d, test_type):
        start_time = time.time()
        manager = multiprocessing.Manager()
        q = manager.Queue()
        nodes = graph.node

        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            future_to_file = dict((executor.submit(calculate, node, graph, nodes_data, cls, q, poly1d, test_type), node) for node in nodes)
            for future in concurrent.futures.as_completed(future_to_file):
                f = future_to_file[future]
                if future.exception() is not None:
                    print('%r generated an exception: %s' % (f, future.exception()))

            with open('Wyniki\\results_with_' + test_type + '.csv', 'wb') as csvfile:
                print "Zapis do pliku"
                writer = csv.writer(csvfile)
                writer.writerow(['Node_1', 'Node_2', test_type + '_sum'])
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

    @classmethod
    def _normalize(cls, matrix):
        return matrix/matrix.sum(axis=0)

    @classmethod
    def _denormalize(cls, matrix, matrix_sum):
        return matrix * matrix_sum

    @classmethod
    def _create_edge_matrix(cls, graph):
        matrix = np.empty((303, 303))
        matrix.fill(0.)
        for edge_start in graph.edge:
            for edge_stop in graph.edge[edge_start]:
                matrix[int(edge_start)][int(edge_stop)] = 1
        return matrix

    @classmethod
    def _create_node_matrix(cls, graph):
        matrix = np.empty((303, 2))
        matrix.fill(0.)
        for node in graph.node:
            matrix[int(node)][0] = graph.node[node]['entry']
            matrix[int(node)][1] = graph.node[node]['exit']
        return matrix

    @classmethod
    def _set_new_value_to_nodes(cls, graph, new_value):
        for node in graph.node:
            graph.node[node]['entry_exit'] = new_value[int(node)][0] + new_value[int(node)][1]

    @classmethod
    def compute_belief_propagation(cls, graph):
        np.set_printoptions(suppress=True)
        edge_matrix = cls._create_edge_matrix(graph)
        node_matrix = cls._create_node_matrix(graph)
        matrix_sum = node_matrix.sum(axis=0)
        #utils.save_to_file('Wyniki/started_value.csv', node_matrix)

        for i in range(100):
            x_old = node_matrix[1][0]
            node_matrix = np.dot(edge_matrix, node_matrix)
            node_matrix = cls._normalize(node_matrix)
            x_new = node_matrix[1][0]
            if abs((x_new - x_old)/x_old) < 0.0000005:
                break

        denormalized = cls._denormalize(node_matrix, matrix_sum)
        cls._set_new_value_to_nodes(graph, node_matrix)
        #utils.save_to_file('Wyniki/denormalized.csv', denormalized)
        #utils.save_to_file('Wyniki/normalized.csv', node_matrix)


def calculate(i, graph, nodes_data, graphmethod, q, poly1d, test_type):
    for j in graph.node:
        if j not in graph.neighbors(i):
            new_network_sum = 0
            graph_temp = copy.deepcopy(graph)
            dist = graphmethod.calculate_edge_length(i, j, nodes_data)
            graph_temp.add_edge(i, j, weight=poly1d(dist))
            graph_temp.add_edge(j, i, weight=poly1d(dist))

            if test_type == 'travelers':
                graphmethod.compute_belief_propagation(graph_temp)
                new_network_sum = graphmethod.find_shortest_path_travelers(graph_temp)
            elif test_type == 'time':
                new_network_sum = graphmethod.dijkstra_weight(graph_temp)
            elif test_type == 'entropy':
                for i in graph_temp.node:
                    graph_temp.node[i]['popularity'] = len(graph_temp.neighbors(i))
                entropy_sum = graphmethod.find_shortest_path_entropy(graph_temp)
                graphmethod.set_edges_weight(graph_temp, entropy_sum)
                new_network_sum = graphmethod.dijkstra_weight(graph_temp)

            result = (i, j, new_network_sum)
            q.put(result)
            print 69615 - q.qsize()
