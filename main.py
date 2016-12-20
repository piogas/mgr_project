from NetworkXResolver import NetworkXResolver
import matplotlib.pyplot as plt
import utils

if __name__ == '__main__':
    #utils.merge_edge_files_data()
    networkX = NetworkXResolver()
    # networkX.init_path('resources/london_transport_multiplex.edges', 'resources/london_transport_nodes.txt')
    networkX.init_path('resources_with_time/merged/lines.csv', 'resources_with_time/merged/stations.csv')
    networkX.draw_graph()
    #networkX.calculate_all_edges_length()
    #etworkX.get_dijkstra_result()
    #networkX.show_km_by_quantity_plot()
    #networkX.show_km_by_time_plot()
    plt.show()


