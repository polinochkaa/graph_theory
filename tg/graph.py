class Node:
    def __init__(self, value):
        self.value = value
        self.neighbors = {}

    def add_neighbor(self, neighbor, weight=None):
        self.neighbors[neighbor] = weight

    def remove_neighbor(self, neighbor):
        if neighbor in self.neighbors:
            del self.neighbors[neighbor]
        else:
            raise ValueError(f"Neighbor with node {neighbor.value} not found.")


class Graph:
    def __init__(self, directed=False, weighted=False):
        self.nodes = {}
        self.directed = directed
        self.weighted = weighted

    def __copy__(self):
        new_graph = Graph(self.directed, self.weighted)
        new_graph.nodes = {value: Node(value) for value in self.nodes}
        for node_value, node in self.nodes.items():
            for neighbor, weight in node.neighbors.items():
                new_graph.nodes[node_value].add_neighbor(new_graph.nodes[neighbor.value], weight)
        return new_graph

    @classmethod
    def from_file(cls, filename):
        graph = None
        try:
            with open(filename, 'r') as file:
                directed = file.readline().strip().lower() == 'true'
                weighted = file.readline().strip().lower() == 'true'
                graph = cls(directed, weighted)
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split()

                        if len(parts) == 1:
                            node_value = parts[0]
                            graph.add_node(node_value)
                        elif len(parts) == 2:
                            node1, node2 = parts
                            graph.add_edge(node1, node2)
                        elif len(parts) == 3:
                            node1, node2, weight = parts
                            graph.add_edge(node1, node2, int(weight))
                        else:
                            raise ValueError(f"Invalid line format: {line}")
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{filename}' not found.")
        except ValueError:
            raise ValueError(f"Invalid data format in file '{filename}'.")
        return graph

    def add_node(self, value):
        if value not in self.nodes:
            self.nodes[value] = Node(value)
        else:
            raise ValueError(f"Node {value} already exists.")

    def add_edge(self, value1, value2, weight=None):
        if value1 not in self.nodes:
            self.add_node(value1)
        if value2 not in self.nodes:
            self.add_node(value2)

        if value1 == value2 and not self.directed:
            raise ValueError(f"Loops are not allowed in undirected graphs.")

        if not self.weighted:
            weight = None

        node1 = self.nodes[value1]
        node2 = self.nodes[value2]

        node1.add_neighbor(node2, weight)

        if not self.directed:
            node2.add_neighbor(node1, weight)

    def remove_node(self, value):
        if value in self.nodes:
            for neighbor in list(self.nodes[value].neighbors):
                self.nodes[value].remove_neighbor(neighbor)
            for node in self.nodes.values():
                if self.nodes[value] in node.neighbors:
                    node.remove_neighbor(self.nodes[value])

            del self.nodes[value]
        else:
            raise ValueError(f"Node {value} does not exist.")

    def remove_edge(self, value1, value2):
        if value1 in self.nodes and value2 in self.nodes:
            node1 = self.nodes[value1]
            node2 = self.nodes[value2]
            node1.remove_neighbor(node2)
            if not self.directed:
                node2.remove_neighbor(node1)
        else:
            raise ValueError(f"One or both of the nodes {value1}, {value2} do not exist.")

    def save_to_file(self, filename):
        try:
            with open(filename, 'w') as file:
                file.write("True\n" if self.directed else "False\n")
                file.write("True\n" if self.weighted else "False\n")
                for node_value, node in self.nodes.items():
                    if node.neighbors:
                        for neighbor, weight in node.neighbors.items():
                            if self.weighted:
                                file.write(f"{node_value} {neighbor.value} {weight}\n")
                            else:
                                file.write(f"{node_value} {neighbor.value}\n")
                    else:
                        is_isolated = True
                        for other_node in self.nodes.values():
                            if node in other_node.neighbors:
                                is_isolated = False
                                break

                        if is_isolated:
                            file.write(f"{node_value}\n")
        except IOError:
            raise IOError(f"Error writing to file '{filename}'")

    def get_edges(self):
        edges = []
        seen_edges = set()

        for node_value, node in self.nodes.items():
            for neighbor, weight in node.neighbors.items():
                if self.directed:
                    if self.weighted:
                        edges.append((node_value, neighbor.value, weight))
                    else:
                        edges.append((node_value, neighbor.value))
                else:
                    edge = tuple(sorted((node_value, neighbor.value)))
                    if edge not in seen_edges:
                        if self.weighted:
                            edges.append((node_value, neighbor.value, weight))
                        else:
                            edges.append((node_value, neighbor.value))
                        seen_edges.add(edge)
        return sorted(edges)

    def get_outgoing_neighbors(self, node_value):
        if node_value in self.nodes:
            return [neighbor.value for neighbor in self.nodes[node_value].neighbors]
        else:
            raise ValueError(f"Node {node_value} does not exist")

    def get_non_adjacent_nodes(self, node_value):
        if node_value not in self.nodes:
            raise ValueError(f"Node {node_value} does not exist")
        non_adjacent_nodes = []
        for node in self.nodes.values():
            if node_value != node.value and self.nodes[node_value] not in node.neighbors:
                non_adjacent_nodes.append(node.value)

        return sorted(non_adjacent_nodes)

    def remove_edges_between_same_degree_nodes(self):
        new_graph = Graph(directed=self.directed, weighted=self.weighted)

        for node_value in self.nodes.keys():
            new_graph.add_node(node_value)

        for node_value, node in self.nodes.items():
            for neighbor, weight in node.neighbors.items():
                if len(node.neighbors) != len(self.nodes[neighbor.value].neighbors):
                    new_graph.add_edge(node_value, neighbor.value, weight)
        return new_graph

    def is_tree_or_forest_bfs(self):
        if not self.directed:
            raise ValueError("This method is applicable only for directed graphs.")

        visited = set()
        components = 0

        def bfs(start, data):
            queue = [start]
            parent = {start: None}
            local_visited = set()

            while queue:
                node = queue.pop(0)
                if node in local_visited:
                    continue
                if node in visited:
                    data['flag'] = True
                local_visited.add(node)
                visited.add(node)

                for neighbor in self.nodes[node].neighbors:
                    neighbor_value = neighbor.value
                    if neighbor_value not in local_visited:
                        queue.append(neighbor_value)
                        parent[neighbor_value] = node
                    elif parent[node] != neighbor_value:
                        return False

            return True

        for node in self.nodes:
            if node not in visited:
                components += 1
                data = {'flag': False}
                bfs_bool = bfs(node, data)
                if data['flag']:
                    components -= 1
                if not bfs_bool:
                    raise ValueError("The graph contains a cycle and is neither a tree nor a forest.")

        return components

    def find_common_nodes_same_distance_dfs(self, u, v):
        def dfs(node, path, all_paths):
            path = path + [node]
            if node not in all_paths:
                all_paths[node] = []
            all_paths[node].append(path)
            for neighbor in self.nodes[node].neighbors:
                if neighbor.value not in path:
                    dfs(neighbor.value, path, all_paths)

        paths_from_u = {}
        paths_from_v = {}

        if u not in self.nodes:
            raise ValueError(f"Node {u} does not exist in the graph.")
        if v not in self.nodes:
            raise ValueError(f"Node {v} does not exist in the graph.")

        dfs(u, [], paths_from_u)
        dfs(v, [], paths_from_v)

        equal_distance_nodes = []

        for node in paths_from_u:
            if node in paths_from_v:
                all_lengths_from_u = {len(path) for path in paths_from_u[node]}
                all_lengths_from_v = {len(path) for path in paths_from_v[node]}
                if all_lengths_from_u == all_lengths_from_v:
                    equal_distance_nodes.append(node)

        if not equal_distance_nodes:
            raise ValueError("No vertices with equal path lengths from both u and v.")

        return equal_distance_nodes

    def prim_mst(self):
        if not self.nodes:
            raise ValueError("Graph is empty. Cannot compute MST.")
        if self.directed:
            raise ValueError("Prim's algorithm works only for undirected graphs.")
        if not self.weighted:
            raise ValueError("Prim's algorithm works only for weighted graphs.")
        mst_edges = []
        total_weight = 0
        visited = set()
        nodes = list(self.nodes.keys())

        current_node = nodes[0]
        visited.add(current_node)

        while len(visited) < len(self.nodes):
            min_edge = None
            min_weight = float('inf')

            for node in visited:
                for neighbor, weight in self.nodes[node].neighbors.items():
                    if neighbor.value not in visited and weight < min_weight:
                        min_edge = (node, neighbor.value)
                        min_weight = weight

            if min_edge is None:
                raise ValueError("The graph is not connected.")

            mst_edges.append((min_edge[0], min_edge[1], min_weight))
            total_weight += min_weight
            visited.add(min_edge[1])

        return mst_edges, total_weight


    def dijkstra(self, u):
        if u not in self.nodes:
            raise ValueError(f"The node '{u}' does not exist in the graph.")

        if not self.weighted:
            raise ValueError("This method requires a weighted graph.")

        distances = {node: float('inf') for node in self.nodes}
        path_counts = {node: 0 for node in self.nodes}
        paths = {node: [] for node in self.nodes}

        distances[u] = 0
        path_counts[u] = 1
        paths[u] = [[u]]
        unvisited = list(self.nodes.keys())

        while unvisited:
            current_node = None
            current_distance = float('inf')
            for node in unvisited:
                if distances[node] < current_distance:
                    current_distance = distances[node]
                    current_node = node

            if current_node is None:
                break
            unvisited.remove(current_node)

            for neighbor, weight in self.nodes[current_node].neighbors.items():
                new_distance = distances[current_node] + weight

                if new_distance < distances[neighbor.value]:
                    distances[neighbor.value] = new_distance
                    path_counts[neighbor.value] = path_counts[current_node]

                    paths[neighbor.value] = [
                        path + [neighbor.value] for path in paths[current_node]
                    ]
                elif new_distance == distances[neighbor.value]:
                    path_counts[neighbor.value] += path_counts[current_node]

                    paths[neighbor.value].extend(
                        path + [neighbor.value] for path in paths[current_node]
                    )

        return distances, path_counts, paths

    def floyd_warshall(self):
        if not self.weighted:
            raise ValueError("This method requires a weighted graph.")

        nodes = list(self.nodes.keys())
        node_indices = {node: idx for idx, node in enumerate(nodes)}
        n = len(nodes)

        dist = [[float('inf')] * n for i in range(n)]
        for i in range(n):
            dist[i][i] = 0

        for node in self.nodes:
            for neighbor, weight in self.nodes[node].neighbors.items():
                dist[node_indices[node]][node_indices[neighbor.value]] = weight

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] < float('inf') and dist[k][j] < float('inf'):
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

        negative_cycle_pairs = set()
        for k in range(n):
            if dist[k][k] < 0:
                for i in range(n):
                    for j in range(n):
                        if dist[i][k] < float('inf') and dist[k][j] < float('inf'):
                            negative_cycle_pairs.add((nodes[i], nodes[j]))

        return sorted(negative_cycle_pairs)

    def bellman_ford(self, u, v, k):
        if u not in self.nodes or v not in self.nodes:
            raise ValueError(f"One or both of the nodes '{u}' or '{v}' do not exist in the graph.")

        all_paths = [(0, (u,))]

        for i in range(len(self.nodes) - 1):
            new_paths = []
            for path_cost, path in all_paths:
                last_node = path[-1]

                for neighbor, weight in self.nodes[last_node].neighbors.items():
                    neighbor_value = neighbor.value
                    new_path = path + (neighbor_value,)
                    new_cost = path_cost + weight
                    new_paths.append((new_cost, new_path))

            all_paths.extend(new_paths)
            all_paths = list(set(all_paths))

        valid_paths = [(cost, path) for cost, path in all_paths if path[-1] == v]
        valid_paths.sort(key=lambda x: x[0])

        return [(cost, list(path)) for cost, path in valid_paths[:k]]

    def edmonds_karp(self, source, sink):
        if source not in self.nodes or sink not in self.nodes:
            raise ValueError(f"Source '{source}' or sink '{sink}' does not exist in the graph.")

        capacity = {u: {v.value: 0 for v in self.nodes[u].neighbors} for u in self.nodes}
        for u in self.nodes:
            for v, w in self.nodes[u].neighbors.items():
                capacity[u][v.value] = w
        ostat = {u: {v: capacity[u].get(v, 0) for v in self.nodes} for u in self.nodes}
        flow = {u: {v: 0 for v in self.nodes} for u in self.nodes}

        def bfs():
            parent = {node: None for node in self.nodes}
            parent[source] = source
            queue = [source]

            while queue:
                current = queue.pop(0)
                for neighbor, cap in ostat[current].items():
                    if cap > 0 and parent[neighbor] is None:
                        parent[neighbor] = current
                        if neighbor == sink:
                            return parent
                        queue.append(neighbor)
            return None

        max_flow = 0
        while True:
            path = bfs()
            if not path:
                break
            path_flow = float('inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, ostat[path[s]][s])
                s = path[s]

            v = sink
            while v != source:
                u = path[v]
                ostat[u][v] -= path_flow
                flow[u][v] += path_flow
                v = u

            max_flow += path_flow

        return max_flow, flow
