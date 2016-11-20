import networkx as nx


class Dijsktra:

    @classmethod
    def dijkstra(cls, G):
        sum_all_paths = 0
        for x in G.node:
            sum_all_paths += cls._calculate_paths_sum(nx.single_source_dijkstra_path_length(G, x))
        print sum_all_paths

    @classmethod
    def _calculate_paths_sum(cls, tab):
        paths_sum = 0
        for i in tab:
            paths_sum += tab[i]
        return paths_sum
