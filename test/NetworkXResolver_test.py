import unittest
import networkx as nx
from project.NetworkXResolver import NetworkXResolver


class TestNetworkXResolverClass(unittest.TestCase):

    def test_read_file(self):
        text = NetworkXResolver.read_from_file('test_resources/test.txt')
        self.assertEqual(text, 'testowy tekst')

    def test_crete_graph(self):
        test_nodes = [(1, 2)]
        new_graph = nx.DiGraph()
        new_graph.add_edges_from(test_nodes)
        test_graph = NetworkXResolver.create_graph(test_nodes)
        self.assertTrue(nx.is_isomorphic(new_graph, test_graph, node_match=None, edge_match=None))

    def test_string_to_edges(self):
        test_string = '1 1 2 2 1 1 3 2 1 2 3 1 2 3 4 2'
        good_result = [('1', '2', {'weight': 2, 'layer': 1}), ('1', '3', {'weight': 2, 'layer': 1}),
                       ('2', '3', {'weight': 1, 'layer': 1}), ('3', '4', {'weight': 2, 'layer': 2})]
        result = NetworkXResolver.create_edges_from_string(test_string)
        self.assertEqual(good_result, result)

    def test_string_to_nodes(self):
        test_string = 'nodeID nodeLabel nodeLat nodeLong 0 abbeyroad 51.531951985733 0.0037377856069111 ' \
                      '1 westham 51.52852551818 0.0053318072586749 ' \
                      '2 actoncentral 51.508757812012 -0.26341579231596'
        good_result = {'0': (0.0037377856069111, 51.531951985733),
                       '1': (0.0053318072586749, 51.52852551818),
                       '2': (-0.26341579231596, 51.508757812012)}
        result = NetworkXResolver.create_nodes_from_string(test_string)
        self.assertEqual(good_result, result)

    def test_share_on_the_type(self):
        test_table = [('1', '2', {'weight': 2, 'layer': 1}), ('1', '3', {'weight': 2, 'layer': 1}),
                      ('2', '3', {'weight': 1, 'layer': 1}), ('3', '4', {'weight': 2, 'layer': 2})]
        good_result = {'blue_edges': [],
                       'green_edges': [
                           ('1', '2', {'weight': 2, 'layer': 1}),
                           ('1', '3', {'weight': 2, 'layer': 1}),
                           ('2', '3', {'weight': 1, 'layer': 1})
                       ],
                       'red_edges': [
                           ('3', '4', {'weight': 2, 'layer': 2})
                       ]}
        result = NetworkXResolver.share_on_the_type(test_table)
        self.assertEqual(result, good_result)

    def test_calculate_edge_length(self):
        networkx = NetworkXResolver('test_resources/london_transport_multiplex.edges',
                                    'test_resources/london_transport_nodes.txt')
        networkx.draw_graph()
        result = networkx.calculate_edge_length(0, 2)
        print "rezultat:"
        self.assertEqual(result, 29.818)
