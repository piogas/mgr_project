import networkx as nx
import math
import copy
import time
import xlwt
import scipy.stats
import numpy as np
import csv


class GraphMethod:

    @classmethod
    def __init__(cls):
        print 'Init GraphMethod'

    @classmethod
    def dijkstra(cls, G):
        sum_all_paths = 0
        for x in G.node:
            sum_all_paths += cls._calculate_paths_sum(nx.single_source_dijkstra_path_length(G, x))
        return sum_all_paths

    @classmethod
    def find_shortest_path(cls, G, nodes_data):
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

        with open('nodes_with_entropy.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Node', 'Popularity', 'Entropy_sum', 'Betweeness'])
            for x in G.node:
                writer.writerow([x, G.node[x]['popularity'], G.node[x]['entropy_sum'], G.node[x]['betweeness']])



    @classmethod
    def _calculate_paths_sum(cls, tab):
        paths_sum = 0
        for i in tab:
            paths_sum += tab[i]
        return paths_sum

    @classmethod
    def depth_first_search(cls, G, nodes_data):
        start_time = time.time()
        result = xlwt.Workbook(encoding="utf-8")
        sheet1 = result.add_sheet("Results")
        style1 = xlwt.easyxf(num_format_str='0')
        style2 = xlwt.easyxf(num_format_str='0.00')
        sheet1.write(0, 0, "NO")
        sheet1.write(0, 1, "Node1")
        sheet1.write(0, 2, "Node1")
        sheet1.write(0, 3, "Length")
        sheet1.write(0, 4, "Match!")

        shortest = cls.dijkstra(G)
        iterations = 0

        #print G.edge
        for i in G.node:
            for j in G.node:
                if j not in G.neighbors(i):
                    iterations += 1
                    #print "Iteration: {} from 90506 --> {} to the end".format(iterations, 90506 - iterations)
                    G_temp = copy.deepcopy(G)
                    dist = cls._calculate_edge_length(i, j, nodes_data)
                    G_temp.add_edge(i, j, weight=dist)
                    G_temp.add_edge(j, i, weight=dist)
                    new_network_sum = cls.dijkstra(G_temp)
                    if iterations == 65000:
                        sheet1 = result.add_sheet("Results_2")
                        result.save("results1.xls")
                        iterations -= 65000

                    # save to xls
                    sheet1.write(iterations, 0, iterations, style1)
                    sheet1.write(iterations, 1, i, style1)
                    sheet1.write(iterations, 2, j, style1)
                    sheet1.write(iterations, 3, new_network_sum, style2)

                    if new_network_sum < shortest:
                        shortest = new_network_sum
                        sheet1.write(iterations, 4, "Match!")
                        #print "SHORTEST! {} n1: {} n2: {}".format(shortest, i, j)

        #print "Iterations: {} from 90506 --> {} to the end".format(iterations, 90506 - iterations)

        print("--- %s seconds ---" % (time.time() - start_time))
        result.save("results1.xls")

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
    def _calculate_edge_length(cls, node_1, node_2, nodes_data):
        lat1 = nodes_data[str(node_1)][0]
        lon1 = nodes_data[str(node_1)][1]
        lat2 = nodes_data[str(node_2)][0]
        lon2 = nodes_data[str(node_2)][1]

        distance = cls.get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2)
        return distance

