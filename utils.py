def merge_node_files_data():
    nodes_str = read_from_file('resources_with_time/underground-stations.csv')
    stations_str = read_from_file('resources_with_time/entry_exit.csv')
    nodes = create_nodes_from_string(nodes_str)
    stations = create_exit_entry_from_string(stations_str)
    missing, missing_node = merge(nodes, stations)
    write_to_file('resources_with_time/merged/', 'missing_stations.csv', 'stations.csv', stations)
    write_to_file('resources_with_time/merged/', 'missing_nodes.csv', 'nodes.csv', nodes)


def merge_edge_files_data():
    travel_time = read_from_file('resources_with_time/underground-travel-time.csv')
    stations_str = read_from_file('resources_with_time/merged/stations.csv')
    edge = create_edges_from_string(travel_time)
    stations = create_nodes_from_string_for_edge(stations_str)
    found_edges = merge_edge(edge, stations)
    write_to_file_edges('resources_with_time/merged/', 'lines.csv', found_edges)
    #write_to_file('resources_with_time/merged/', 'missing_nodes.csv', 'nodes.csv', nodes)


def create_edges_from_string(string_data):
        string_data = string_data.split()
        edges = []
        for i in range(0, len(string_data), 4):
            edges.append((string_data[i], string_data[i + 1],
                          {'weight': int(string_data[i + 3]), 'layer': int(string_data[i + 2]), 'length': {}}))
        return edges


def read_from_file(uri_to_file):
    with open(uri_to_file) as content_file:
        content = content_file.read()
        content_file.close()
        return content


def merge_edge(edges, stations):
    found = []
    for edge in edges:
        if edge[1] in stations and edge[0] in stations:
            found.append(edge)
    return found


def merge(nodes, stations):
    missing = []
    missing_node = []
    for station in stations:
        if station in nodes:
            stations[station].append(nodes[station][0])
            stations[station].append(nodes[station][1])
            stations[station].append(nodes[station][2])
            nodes[station].append(stations[station][0])
            nodes[station].append(stations[station][1])
        else:
            missing.append(station)
    print nodes
    for node in nodes:
        if len(nodes[node]) == 2:
            missing_node.append(node)
    return missing, missing_node


def write_to_file(uri_to_file, missing, good, data):
    with open(uri_to_file + good, 'w') as content_file:
        for row in data:
            if len(data[row]) == 5 or len(data[row]) == 4:
                if len(data[row]) == 5:
                    content_file.write(str(data[row][4]))
                    content_file.write(';')
                content_file.write(row)
                content_file.write(';')
                content_file.write(str(data[row][0]))
                content_file.write(';')
                content_file.write(str(data[row][1]))
                content_file.write(';')
                content_file.write(str(data[row][2]))
                content_file.write(';')
                content_file.write(str(data[row][3]))
                content_file.write(';\n')

    with open(uri_to_file + missing, 'w') as content_file:
        for row in data:
            if len(data[row]) == 3 or len(data[row]) == 2:
                content_file.write(row)
                content_file.write(';')
                content_file.write(str(data[row][0]))
                content_file.write(';')
                content_file.write(str(data[row][1]))
                content_file.write(';\n')

        content_file.close()


def write_to_file_edges(uri_to_file, good, data):
    with open(uri_to_file + good, 'w') as content_file:
        for row in data:
            print row[2]
            content_file.write(str(row[0]))
            content_file.write(';')
            content_file.write(str(row[1]))
            content_file.write(';')
            content_file.write(str(row[2]['layer']))
            content_file.write(';')
            content_file.write(str(row[2]['weight']))
            content_file.write(';\n')

        content_file.close()


def create_nodes_from_string(string_data):
    string_data = string_data.split(",")
    nodes = {}
    for i in range(0, len(string_data), 8):
        node_data = [float(string_data[i + 2]), float(string_data[i + 1]), string_data[i]]
        nodes[string_data[i+3]] = node_data
    return nodes


def create_nodes_from_string_for_edge(string_data):
    string_data = string_data.split(";")
    nodes = []
    for i in range(0, len(string_data), 6):
        nodes.append(string_data[i])
    return nodes


def create_exit_entry_from_string(string_data):
    string_data = string_data.split(";")
    stations = {}
    for i in range(0, len(string_data), 12):
        node_data = [float(string_data[i + 10]), float(string_data[i + 11])]
        stations[string_data[i]] = node_data
    return stations


def save_to_file(uri_to_file, data):
    with open(uri_to_file, 'w') as content_file:
        content_file.write(str(data))