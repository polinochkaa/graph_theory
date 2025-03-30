from collections import deque
import heapq
import math

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
            raise ValueError(f"Сосед с номером {neighbor.value} не найден.")

class Graph:
    def __init__(self, directed=True, weighted=True):
        self.nodes = {}  # Изменяем на словарь, где ключ - имя вершины, значение - тип (склад/клиент)
        self.edges = []  # список рёбер (from_vertex, to_vertex, weight)
        self.directed = directed
        self.weighted = weighted

    def add_node(self, node, node_type):
        """Добавляет вершину в граф с указанным типом (склад/клиент)."""
        if node in self.nodes:
            raise ValueError(f"Вершина {node} уже существует в графе")
        if node_type not in ['warehouse', 'client']:
            raise ValueError("Тип вершины должен быть 'warehouse' или 'client'")
        self.nodes[node] = node_type

    def remove_node(self, node):
        """Удаляет вершину и все связанные с ней рёбра."""
        if node not in self.nodes:
            raise ValueError(f"Вершина {node} не существует в графе")
        
        # Удаляем все рёбра, связанные с этой вершиной
        self.edges = [edge for edge in self.edges if edge[0] != node and edge[1] != node]
        del self.nodes[node]

    def add_edge(self, node1, node2, cost=0, delivery_time=0):
        """
        Добавляет ребро между двумя вершинами с указанием стоимости и времени доставки
        
        :param node1: Начальная вершина
        :param node2: Конечная вершина
        :param cost: Стоимость доставки в рублях
        :param delivery_time: Время доставки в часах
        """
        if node1 not in self.nodes or node2 not in self.nodes:
            raise ValueError("Обе вершины должны существовать в графе перед добавлением ребра")
        
        if not isinstance(cost, (int, float)) or not isinstance(delivery_time, (int, float)):
            raise ValueError("Стоимость и время доставки должны быть числами")
        
        if cost < 0 or delivery_time < 0:
            raise ValueError("Стоимость и время доставки не могут быть отрицательными")
        
        # Проверяем, существует ли уже такое ребро
        for edge in self.edges:
            if edge[0] == node1 and edge[1] == node2:
                # Если ребро существует, обновляем его параметры
                self.edges.remove(edge)
                break
        
        # Добавляем новое ребро
        self.edges.append((node1, node2, cost, delivery_time))
        
        # Для неориентированного графа добавляем обратное ребро
        if not self.directed and node1 != node2:
            # Проверяем существование обратного ребра
            for edge in self.edges:
                if edge[0] == node2 and edge[1] == node1:
                    self.edges.remove(edge)
                    break
            
            self.edges.append((node2, node1, cost, delivery_time))

    def remove_edge(self, from_vertex, to_vertex):
        """Удаляет ребро из графа."""
        if from_vertex not in self.nodes:
            raise ValueError(f"Начальная вершина {from_vertex} не существует в графе")
        if to_vertex not in self.nodes:
            raise ValueError(f"Конечная вершина {to_vertex} не существует в графе")

        # Ищем ребро для удаления
        initial_length = len(self.edges)
        self.edges = [edge for edge in self.edges if not (edge[0] == from_vertex and edge[1] == to_vertex)]
        
        if not self.directed:
            # Для неориентированного графа удаляем также обратное ребро
            self.edges = [edge for edge in self.edges if not (edge[0] == to_vertex and edge[1] == from_vertex)]

        if len(self.edges) == initial_length:
            raise ValueError(f"Ребро от {from_vertex} к {to_vertex} не существует в графе")

    def get_neighbors(self, value):
        """Возвращает список соседей вершины."""
        if value not in self.nodes:
            raise ValueError(f"Вершина {value} не существует в графе")
        neighbors = []
        for edge in self.edges:
            if edge[0] == value:
                neighbors.append(edge[1])
        return sorted(neighbors)

    def get_nodes(self):
        """Возвращает отсортированный список всех вершин."""
        return sorted(list(self.nodes.keys()))

    def get_edges(self):
        """Возвращает список всех рёбер."""
        edges = []
        for edge in self.edges:
            if self.directed or edge[0] < edge[1]:
                edges.append(edge)
        return sorted(edges)

    def dfs(self, start_value, visited=None):
        if start_value not in self.nodes:
            raise ValueError(f"Стартовая вершина {start_value} не существует")

        if visited is None:
            visited = set()

        visited.add(start_value)
        result = [start_value]

        for neighbor in sorted(self.get_neighbors(start_value)):
            if neighbor not in visited:
                result.extend(self.dfs(neighbor, visited))

        return result

    def bfs(self, start_value):
        if start_value not in self.nodes:
            raise ValueError(f"Стартовая вершина {start_value} не существует")

        visited = set([start_value])
        queue = deque([start_value])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in sorted(self.get_neighbors(current)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

    def dijkstra(self, start_value):
        if not self.weighted:
            raise ValueError("Алгоритм Дейкстры требует взвешенный граф")
        if start_value not in self.nodes:
            raise ValueError(f"Стартовая вершина {start_value} не существует")

        distances = {node: float('infinity') for node in self.nodes}
        distances[start_value] = 0
        unvisited = set(self.nodes)

        while unvisited:
            current = min(unvisited, key=lambda x: distances[x])
            if distances[current] == float('infinity'):
                break

            for neighbor in self.get_neighbors(current):
                for edge in self.edges:
                    if edge[0] == current and edge[1] == neighbor:
                        weight = edge[2]
                        distance = distances[current] + weight
                        if distance < distances[neighbor]:
                            distances[neighbor] = distance

            unvisited.remove(current)

        return distances

    def find_path(self, start_value, end_value):
        if start_value not in self.nodes or end_value not in self.nodes:
            raise ValueError("Стартовая или конечная вершина не существует")

        visited = set()
        path = []

        def dfs_path(current_value):
            if current_value == end_value:
                return True

            visited.add(current_value)
            path.append(current_value)

            for neighbor in sorted(self.get_neighbors(current_value)):
                if neighbor not in visited:
                    if dfs_path(neighbor):
                        return True

            path.pop()
            return False

        if dfs_path(start_value):
            path.append(end_value)
            return path
        return None

    def get_non_adjacent_nodes(self, node_value):
        if node_value not in self.nodes:
            raise ValueError(f"Вершина {node_value} не существует")
        non_adjacent_nodes = []
        for node in self.nodes:
            if node_value != node and node not in self.get_neighbors(node_value):
                non_adjacent_nodes.append(node)

        return sorted(non_adjacent_nodes)

    def is_connected(self):
        if not self.nodes:
            return True

        start_node = next(iter(self.nodes))
        visited = set()

        def dfs_connected(node_value):
            visited.add(node_value)
            for neighbor in self.get_neighbors(node_value):
                if neighbor not in visited:
                    dfs_connected(neighbor)

        dfs_connected(start_node)
        return len(visited) == len(self.nodes)

    def find_cycles(self):
        visited = set()
        cycles = []
        path = []
        path_set = set()

        def dfs_cycle(node_value):
            visited.add(node_value)
            path.append(node_value)
            path_set.add(node_value)

            for neighbor in sorted(self.get_neighbors(node_value)):
                if neighbor not in visited:
                    if dfs_cycle(neighbor):
                        return True
                elif neighbor in path_set:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:])
                    return True

            path_set.remove(node_value)
            path.pop()
            return False

        for node in sorted(self.nodes):
            if node not in visited:
                dfs_cycle(node)

        return cycles

    def kruskal(self):
        if not self.weighted:
            raise ValueError("Алгоритм Краскала требует взвешенный граф")
        if self.directed:
            raise ValueError("Алгоритм Краскала работает только для неориентированных графов")

        def find(parent, i):
            if parent[i] != i:
                parent[i] = find(parent, parent[i])
            return parent[i]

        def union(parent, rank, x, y):
            root_x = find(parent, x)
            root_y = find(parent, y)
            if rank[root_x] < rank[root_y]:
                parent[root_x] = root_y
            elif rank[root_x] > rank[root_y]:
                parent[root_y] = root_x
            else:
                parent[root_y] = root_x
                rank[root_x] += 1

        edges = []
        for edge in self.edges:
            if edge[0] < edge[1]:  # Avoid duplicates
                edges.append((edge[2], edge[0], edge[1]))
        edges.sort()  # Sort by weight

        mst_edges = []
        total_weight = 0
        parent = {node: node for node in self.nodes}
        rank = {node: 0 for node in self.nodes}

        for weight, u, v in edges:
            if find(parent, u) != find(parent, v):
                union(parent, rank, u, v)
                mst_edges.append((u, v, weight))
                total_weight += weight

        return mst_edges, total_weight

    def prim(self):
        if not self.weighted:
            raise ValueError("Алгоритм Прима требует взвешенный граф")
        if self.directed:
            raise ValueError("Алгоритм Прима работает только для неориентированных графов")
        if not self.is_connected():
            raise ValueError("Граф должен быть связным для алгоритма Прима")

        start_node = next(iter(self.nodes))
        visited = {start_node}
        mst_edges = []
        total_weight = 0

        while len(visited) < len(self.nodes):
            min_edge = None
            min_weight = float('infinity')

            for node in visited:
                for neighbor in self.get_neighbors(node):
                    if neighbor not in visited:
                        for edge in self.edges:
                            if edge[0] == node and edge[1] == neighbor:
                                weight = edge[2]
                                if weight < min_weight:
                                    min_edge = (node, neighbor)
                                    min_weight = weight

            if min_edge is None:
                raise ValueError("Граф не связан.")

            mst_edges.append((min_edge[0], min_edge[1], min_weight))
            total_weight += min_weight
            visited.add(min_edge[1])

        return mst_edges, total_weight

    def edmonds_karp(self, source, sink):
        if source not in self.nodes or sink not in self.nodes:
            raise ValueError(f"Источник '{source}' или сток '{sink}' не существует в графе.")

        # Резервный граф инициализируется напрямую из весов рёбер
        residual = {u: {v: 0 for v in self.nodes} for u in self.nodes}
        for edge in self.edges:
            residual[edge[0]][edge[1]] = edge[2] if edge[2] is not None else 1

        flow = {u: {v: 0 for v in self.nodes} for u in self.nodes}
        max_flow = 0

        def bfs():
            parent = {node: None for node in self.nodes}
            parent[source] = source
            queue = [source]

            while queue:
                current = queue.pop(0)
                for neighbor, cap in residual[current].items():
                    if cap > 0 and parent[neighbor] is None:  # Не посещён
                        parent[neighbor] = current
                        if neighbor == sink:
                            return parent
                        queue.append(neighbor)
            return None

        # Ищем увеличивающие пути
        while True:
            parent_map = bfs()
            if not parent_map:
                break

            # Находим минимальную пропускную способность в пути
            path_flow = float('inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, residual[parent_map[s]][s])
                s = parent_map[s]

            # Обновляем резервный граф и поток
            v = sink
            while v != source:
                u = parent_map[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                flow[u][v] += path_flow
                flow[v][u] -= path_flow
                v = u

            max_flow += path_flow

        return max_flow, flow

    def find_shortest_path(self, start, end, weight_type='cost'):
        """
        Публичный метод для нахождения кратчайшего пути
        
        :param start: начальная вершина
        :param end: конечная вершина
        :param weight_type: тип веса ('cost' или 'delivery_time')
        :return: кортеж (путь, общий вес)
        """
        if start not in self.nodes or end not in self.nodes:
            raise ValueError("Начальная или конечная вершина не существует в графе")

        # Инициализация
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous_nodes = {node: None for node in self.nodes}
        pq = [(0, start)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            # Если достигли конечной вершины
            if current_node == end:
                break

            # Если текущее расстояние больше уже известного, пропускаем
            if current_distance > distances[current_node]:
                continue

            # Проверяем все ребра из текущей вершины
            for edge in self.edges:
                if edge[0] == current_node:
                    neighbor = edge[1]
                    # Выбираем вес в зависимости от параметра
                    weight = edge[2] if weight_type == 'cost' else edge[3]
                    
                    distance = current_distance + weight

                    # Если нашли более короткий путь
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous_nodes[neighbor] = current_node
                        heapq.heappush(pq, (distance, neighbor))

        # Восстанавливаем путь
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous_nodes[current]
        path.reverse()

        return path, distances[end]

    def find_optimal_path(self, start, end):
        """
        Публичный метод для нахождения Парето-оптимального пути
        
        :param start: начальная вершина
        :param end: конечная вершина
        :return: кортеж (путь, стоимость, время)
        """
        if start not in self.nodes or end not in self.nodes:
            raise ValueError("Начальная или конечная вершина не существует в графе")

        # Инициализация
        distances_cost = {node: float('inf') for node in self.nodes}
        distances_time = {node: float('inf') for node in self.nodes}
        distances_cost[start] = 0
        distances_time[start] = 0
        previous_nodes = {node: None for node in self.nodes}
        pq = [(0, 0, start)]  # (стоимость, время, вершина)

        while pq:
            current_cost, current_time, current_node = heapq.heappop(pq)

            # Если достигли конечной вершины
            if current_node == end:
                break

            # Проверяем все ребра из текущей вершины
            for edge in self.edges:
                if edge[0] == current_node:
                    neighbor = edge[1]
                    edge_cost = edge[2]
                    edge_time = edge[3]
                    
                    new_cost = current_cost + edge_cost
                    new_time = current_time + edge_time

                    # Условие Парето-оптимальности
                    if (new_cost < distances_cost[neighbor] or 
                        new_time < distances_time[neighbor]):
                        distances_cost[neighbor] = new_cost
                        distances_time[neighbor] = new_time
                        previous_nodes[neighbor] = current_node
                        heapq.heappush(pq, (new_cost, new_time, neighbor))

        # Восстанавливаем путь
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous_nodes[current]
        path.reverse()

        return path, distances_cost[end], distances_time[end]

    @property
    def edges_list(self):
        return self.edges
