import networkx as nx
import matplotlib.pyplot as plt
import math
from project.Dijkstra import Dijsktra
import numpy as np

__author__ = 'piogas'


class NetworkXResolver:

    edges_table = []
    nodes_data = {}
    # resources/london_transport_multiplex.edges
    edges_path = ''
    # resources/london_transport_nodes.txt
    nodes_path = ''
    graph = nx.Graph()

    dict_length_range = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}
    dict_length_range_label = ['0-0.5km', '0.5-1km', '1-1.5km', '1.5-2km', '2-2.5km', '2.5-3km', '3-3.5km', '3.5-4km',
                               '4-4.5km', '4.5-5km', '5-5.5km', '>5.5km']

    @classmethod
    def __init__(cls):
        print 'Calling constructor'

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
        pos = nx.spring_layout(cls.graph, pos=cls.nodes_data, fixed=fixed_nodes)
        values = []
        for node in cls.graph.nodes():
            values.append(0.25)
        nx.draw_networkx_nodes(cls.graph, pos, cmap=plt.get_cmap('jet'), node_color=values, node_size=10)
        edges = cls._share_on_the_type(cls.edges_table)
        cls._draw_edges(cls.graph, pos, edges)
        # plt.show()

    @classmethod
    def _upload_data_from_file(cls, edges_file, nodes_file):
        string_edges = cls._read_from_file(edges_file)
        string_nodes = cls._read_from_file(nodes_file)
        return {'string_edges': string_edges, 'string_nodes': string_nodes}

    @classmethod
    def _share_on_the_type(cls, edges_table):
        blue_edges = []
        red_edges = []
        green_edges = []
        for edge in edges_table:
            if edge[2]['layer'] == 1:
                green_edges.append(edge)
            if edge[2]['layer'] == 2:
                red_edges.append(edge)
            if edge[2]['layer'] == 3:
                blue_edges.append(edge)
        return {'blue_edges': blue_edges, 'red_edges': red_edges, 'green_edges': green_edges}

    @classmethod
    def _draw_edges(cls, graph, pos, edges):
        nx.draw_networkx_edges(graph, pos, edgelist=edges['red_edges'], edge_color='r', arrows=False)
        nx.draw_networkx_edges(graph, pos, edgelist=edges['green_edges'], edge_color='g', arrows=False)
        nx.draw_networkx_edges(graph, pos, edgelist=edges['blue_edges'], edge_color='b', arrows=False)

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
        string_data = string_data.split()
        edges = []
        for i in range(0, len(string_data), 4):
            edges.append((string_data[i], string_data[i + 1],
                          {'weight': int(string_data[i + 3]), 'layer': int(string_data[i + 2]), 'length': {}}))
        return edges

    @classmethod
    def _create_nodes_from_string(cls, string_data):
        string_data = string_data.split(",")
        nodes = {}
        for i in range(0, len(string_data), 8):
            # long lat
            node_data = (float(string_data[i + 2]), float(string_data[i + 1]))
            nodes[string_data[i]] = node_data
        return nodes

    @classmethod
    def _calculate_edge_length(cls, node_1, node_2):
        lat1 = cls.nodes_data[str(node_1)][0]
        lon1 = cls.nodes_data[str(node_1)][1]
        lat2 = cls.nodes_data[str(node_2)][0]
        lon2 = cls.nodes_data[str(node_2)][1]

        distance = cls._get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2)
        print cls.graph.edge
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
            distance = cls._get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2)
            edge[2]['length'] = distance
            cls.graph.edge[edge[0]][edge[1]]['length'] = distance
            #cls.graph.edge[edge[1]][edge[0]]['length'] = distance
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
        plt.figure()
        # print cls.dict_length_range.values()
        plt.plot(x, cls.dict_length_range.values())
        plt.grid()
        plt.xticks(x, cls.dict_length_range_label, rotation=45)

    @classmethod
    def show_km_by_time_plot(cls):
        length_and_time = np.array(cls._get_all_length_and_time())
        y = length_and_time[:, 0]
        x = length_and_time[:, 1]
        plt.figure()
        plt.plot(x, y, 'ro')
        plt.grid()
        #plt.xticks(x, y, rotation=45)

    @classmethod
    def _get_all_length_and_time(cls):
        all_length = []
        for x in cls.edges_table:
            all_length.append([x[2]['length'], x[2]['weight']])
        all_length = sorted(all_length, key=lambda item: item[0])
        print all_length
        return all_length

    @classmethod
    def get_dijkstra_result(cls):
        dijkstra = Dijsktra()
        dijkstra.dijkstra(cls.graph)
