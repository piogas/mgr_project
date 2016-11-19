from project.NetworkXResolver import NetworkXResolver
import matplotlib.pyplot as plt

networkX = NetworkXResolver()
networkX.init_path('resources/london_transport_multiplex.edges', 'resources/london_transport_nodes.txt')
networkX.draw_graph()
networkX.calculate_all_edges_length()
networkX.show_plot()
plt.show()
