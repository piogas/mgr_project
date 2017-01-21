# -*- coding: CP1250 -*-

import networkx as nx
import matplotlib.pyplot as plt
import math
from GraphMethod import GraphMethod
import numpy as np
import scipy.stats
import pylab
import sys

pylab.rc('text', usetex=True)
pylab.rc('text.latex',unicode=True)
pylab.rc('text.latex',preamble='\usepackage[T1]{polski}')
import copy
import multiprocessing
from sumproduct import Variable, Factor, FactorGraph
import propagate as prop



__author__ = 'piogas'


class NetworkXResolver:

    test_type = 'time'

    edges_table = []
    nodes_data = {}
    entry_exit = {}
    pos = {}

    test = 1
    # resources/london_transport_multiplex.edges
    edges_path = ''
    # resources/london_transport_nodes.txt
    nodes_path = ''
    lines = {}
    graph = nx.MultiGraph()
    poly1d = {}


    dict_length_range = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}
    dict_length_range_label = ['0-0.5', '0.5-1', '1-1.5', '1.5-2', '2-2.5', '2.5-3', '3-3.5', '3.5-4',
                               '4-4.5', '4.5-5', '5-5.5', '>5.5']

    colors = range(20)

    @classmethod
    def __init__(cls):
        print 'Calling constructor'
        if len(sys.argv) > 1:
            if sys.argv[1] == 't':
                cls.test_type = 'time' #t - arg
            if sys.argv[1] == 'tr':
                cls.test_type = 'travelers' #tr - arc
            if sys.argv[1] == 'e':
                cls.test_type = 'entropy'#e - arc

        print '---- Start "' + cls.test_type + '" method ----'

    @classmethod
    def init_path(cls, edges_path, nodes_path):
        cls.edges_path = edges_path
        cls.nodes_path = nodes_path

    @classmethod
    def draw_graph(cls):
        string_data = cls._upload_data_from_file(cls.edges_path, cls.nodes_path)
        cls.edges_table = cls._create_edges_from_string(string_data['string_edges'])
        cls.nodes_data = cls._create_nodes_from_string(string_data['string_nodes'])
        fixed_nodes = cls.nodes_data.keys()
        cls.graph = cls._create_graph(cls.edges_table)
        cls._set_nodes_levels()
        cls.pos = nx.spring_layout(cls.graph, pos=cls.nodes_data, fixed=fixed_nodes)
        values = []
        for _ in cls.graph.nodes():
            values.append(0.25)
        cls._draw_edges(cls.graph, cls.pos, cls.edges_table)
        nx.draw_networkx_nodes(cls.graph, cls.pos, cmap=plt.get_cmap('jet'), node_color=values, node_size=10)
        cls._set_edges_levels()

    @classmethod
    def _set_nodes_levels(cls):
        for i in cls.graph.node:
            cls.graph.node[i]['popularity'] = len(cls.graph.neighbors(i))
            cls.graph.node[i]['entry'] = cls.entry_exit[i][0]
            cls.graph.node[i]['exit'] = cls.entry_exit[i][1]
            cls.graph.node[i]['pos'] = str(cls.nodes_data[i][0]*300) + ',' + str(cls.nodes_data[i][1]*300) + '!'

    @classmethod
    def _set_edges_levels(cls):
        for i in cls.graph.edges():
            popularity_0 = cls.graph.node[i[0]]['popularity']
            popularity_1 = cls.graph.node[i[1]]['popularity']
            popularity = (popularity_0, popularity_1)
            scipy.stats.entropy(np.asarray(popularity, dtype=float))

    @classmethod
    def _upload_data_from_file(cls, edges_file, nodes_file):
        string_edges = cls._read_from_file(edges_file)
        string_nodes = cls._read_from_file(nodes_file)
        return {'string_edges': string_edges, 'string_nodes': string_nodes}

    @classmethod
    def _draw_edges(cls, graph, pos, edges):
        nx.draw_networkx_edges(graph, pos, edgelist=edges, arrows=False, edge_cmap=plt.cm.datad)
        edges, weights = zip(*nx.get_edge_attributes(cls.graph, 'layer').items())
        nx.draw(cls.graph, pos, node_color='b', edgelist=edges, arrows=False, edge_color=weights, node_size=1,
                width=3.0, edge_cmap=plt.cm.RdYlBu)

    @classmethod
    def _read_from_file(cls, uri_to_file):
        with open(uri_to_file) as content_file:
            content = content_file.read()
            content_file.close()
            return content

    @classmethod
    def _create_graph(cls, data_to_graph):
        new_graph = nx.DiGraph()
        new_graph.add_edges_from(data_to_graph)
        return new_graph

    @classmethod
    def _create_edges_from_string(cls, string_data):
        string_data = string_data.split(";")
        edges = []
        for i in range(0, len(string_data), 4):
            if string_data[i + 2] in cls.lines:
                cls.lines[string_data[i + 2]].append((string_data[i]))
                cls.lines[string_data[i + 2]].append((string_data[i + 1]))
            else:
                cls.lines[string_data[i + 2]] = []
                cls.lines[string_data[i + 2]].append((string_data[i]))
                cls.lines[string_data[i + 2]].append((string_data[i + 1]))

            edges.append((string_data[i], string_data[i + 1],
                          {'weight': int(string_data[i + 3]), 'travel_time': int(string_data[i + 3]),
                           'layer': int(string_data[i + 2]), 'length': {}}))
        return edges

    @classmethod
    def _create_nodes_from_string(cls, string_data):
        string_data = string_data.split(";")
        nodes = {}
        for i in range(0, len(string_data), 6):
            # long lat
            entry_exit = (float(string_data[i + 2]), float(string_data[i + 3]))
            node_data = (float(string_data[i + 4]), float(string_data[i + 5]))
            nodes[string_data[i]] = node_data
            cls.entry_exit[string_data[i]] = entry_exit
        return nodes

    @classmethod
    def _calculate_edge_length(cls, node_1, node_2):
        lat1 = cls.nodes_data[str(node_1)][0]
        lon1 = cls.nodes_data[str(node_1)][1]
        lat2 = cls.nodes_data[str(node_2)][0]
        lon2 = cls.nodes_data[str(node_2)][1]

        distance = cls._get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2)
        return distance

    @classmethod
    def _get_distance_from_lat_lon_in_km(cls, lat1, lon1, lat2, lon2):
        r = 6371
        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = r * c
        return math.ceil(d*1000)/1000

    @classmethod
    def calculate_all_edges_length(cls):
        for edge in cls.edges_table:
            lat1 = cls.nodes_data[str(edge[0])][0]
            lon1 = cls.nodes_data[str(edge[0])][1]
            lat2 = cls.nodes_data[str(edge[1])][0]
            lon2 = cls.nodes_data[str(edge[1])][1]
            distance = GraphMethod.get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2)
            edge[2]['length'] = distance
            cls.graph.edge[edge[0]][edge[1]]['length'] = distance
            cls._assign_to_length_group(distance)

    @classmethod
    def _assign_to_length_group(cls, length):
        length = math.ceil(length*10)/10
        if length <= 0.5:
            cls.dict_length_range[0] += 1
        elif 0.5 < length <= 1:
            cls.dict_length_range[1] += 1
        elif 1 < length <= 1.5:
            cls.dict_length_range[2] += 1
        elif 1.5 < length <= 2:
            cls.dict_length_range[3] += 1
        elif 2 < length <= 2.5:
            cls.dict_length_range[4] += 1
        elif 2.5 < length <= 3:
            cls.dict_length_range[5] += 1
        elif 3 < length <= 3.5:
            cls.dict_length_range[6] += 1
        elif 3.5 < length <= 4:
            cls.dict_length_range[7] += 1
        elif 4 < length <= 4.5:
            cls.dict_length_range[8] += 1
        elif 4.5 < length <= 5:
            cls.dict_length_range[9] += 1
        elif 5 < length <= 5.5:
            cls.dict_length_range[10] += 1
        elif 5.5 < length:
            cls.dict_length_range[11] += 1

    @classmethod
    def show_km_by_quantity_plot(cls):
        x = cls.dict_length_range.keys()
        fig = plt.figure()
        plt.plot(x, cls.dict_length_range.values())
        plt.grid()
        plt.xticks(x, cls.dict_length_range_label)
        plt.xlabel(u'D�ugo�� po��czenia [km]', fontsize=18)
        plt.ylabel(u'Ilo�� wierzcho�k�w', fontsize=16)
        fig.savefig('km_quantity.png')

    @classmethod
    def show_km_by_time_plot(cls):
        length_and_time = np.array(cls._get_all_length_and_time())
        x = length_and_time[:, 0]
        y = length_and_time[:, 1]
        fig = plt.figure()
        plt.plot(x, y, 'ro')
        plt.grid()
        plt.ylabel('Czas przejazdu [s]', fontsize=18)
        plt.xlabel(u'D�ugo�� po��czenia [km]', fontsize=16)

        cls._get_approximation_for_graph()
        fig.savefig('km_time.png')

    @classmethod
    def _get_approximation_for_graph(cls):
        length_and_time = np.array(cls._get_all_length_and_time())
        x = length_and_time[:, 0]
        y = length_and_time[:, 1]
        xz = np.array(x)
        yz = np.array(y)
        z = np.polyfit(xz, yz, 3)
        cls.poly1d = np.poly1d(z)
        print(np.poly1d(cls.poly1d))
        app_x = []
        app_y = []
        for i in range(0, 13):
            app_y.append(cls.poly1d(i))
            app_x.append(i)

        plt.plot(app_x, app_y, '--')

    @classmethod
    def _get_all_length_and_time(cls):
        all_length = []
        for x in cls.edges_table:
            all_length.append([x[2]['length'], x[2]['weight']])
        all_length = sorted(all_length, key=lambda item: item[0])
        return all_length

    @classmethod
    def get_dijkstra_result(cls):
        cls.graph.edge
        cls._get_approximation_for_graph()
        graph_method = GraphMethod()
        graph_method.compute_belief_propagation(cls.graph)
        #graph_method.find_shortest_path_travelers(cls.graph)
        # labels = nx.get_edge_attributes(cls.graph, 'travelers')
        # nx.draw_networkx_edge_labels(cls.graph, cls.pos, edge_labels=labels)
        # node_labels = nx.get_node_attributes(cls.graph, 'entry')
        # nx.draw_networkx_labels(cls.graph, cls.pos, labels = node_labels)
        graph_method.depth_first_search(cls.graph, cls.nodes_data, cls.poly1d, cls.test_type)
        #graph_method.find_shortest_path(cls.graph)