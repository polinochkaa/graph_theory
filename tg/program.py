from graph import Graph

def print_menu():
    print("\nMenu:")
    print("0. Exit")
    print("1. Load graph from file")
    print("2. Create graph from keyboard input")
    print("3. Add node")
    print("4. Add edge")
    print("5. Remove node")
    print("6. Remove edge")
    print("7. Save graph to file")
    print("8. Display edges")
    print("9. Task 2: Show outgoing neighbors")
    print("10. Task 3: Show non-adjacent nodes")
    print("11. Task 4: Remove edges between same degree nodes")
    print("12. Task 5 (BFS): Define if graph a tree or a forest")
    print("13. Task 6 (DFS): Find a node with 2 equal distances")
    print("14. Task 7: Find minimum spanning tree using Prim's algorithm")
    print("15. Task 8: Find the number of shortest paths from a node")
    print("16. Task 9: Find k shortest paths between u and v")
    print("17. Task 10: Find pairs with negative cycles")
    print("18. Task 11: Find max flow")


def get_confirmation(prompt):
    while True:
        choice = input(prompt + " (y/n): ").strip().lower()
        if choice in ['y', 'n']:
            return choice == 'y'

def main():
    graph = None

    while True:
        print_menu()
        choice = input("Choose an option: ")

        if choice.lower() == '0':
            print("Exiting program.")
            break

        try:
            if choice == '1':
                filename = input("Enter the filename to load the graph from: ")
                graph = Graph.from_file(filename)
                print(f"Graph loaded successfully from '{filename}'.")


            elif choice == '2':
                directed = get_confirmation("Is the graph directed?")
                weighted = get_confirmation("Is the graph weighted?")
                graph = Graph(directed, weighted)
                print("You can add edges or isolated nodes.")
                print("To add an edge, enter 'edge'. To add an isolated node, enter 'node'. Type 'done' when finished:")
                while True:
                    line = input()
                    if line.lower() == 'done':
                        break
                    if line.lower() == 'edge':
                        if weighted:
                            value1 = input("Enter the first node of the edge: ")
                            value2 = input("Enter the second node of the edge: ")
                            weight = int(input("Enter the weight of the edge: "))
                            graph.add_edge(value1, value2, weight)
                            print(f"Edge between {value1} and {value2} with weight {weight} added successfully.")
                        else:
                            value1 = input("Enter the first node of the edge: ")
                            value2 = input("Enter the second node of the edge: ")
                            graph.add_edge(value1, value2)
                            print(f"Edge between {value1} and {value2} added successfully.")
                    elif line.lower() == 'node':
                        isolated_node = input("Enter the isolated node value: ")
                        graph.add_node(isolated_node)
                        print(f"Isolated node {isolated_node} added.")

            elif choice == '3':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                node_value = input("Enter the node value to add: ")
                graph.add_node(node_value)
                print(f"Node {node_value} added successfully.")

            elif choice == '4':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                node1 = input("Enter the first node of the edge: ")
                node2 = input("Enter the second node of the edge: ")
                if node1 not in graph.nodes or node2 not in graph.nodes:
                    confirm = get_confirmation("One or both of the nodes do not exist. Do you want to add them?")
                    if not confirm:
                        continue
                weight = None
                if graph.weighted:
                    weight = int(input("Enter the weight of the edge: "))
                graph.add_edge(node1, node2, weight)
                print(f"Edge between {node1} and {node2} added successfully.")

            elif choice == '5':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                node_value = input("Enter the node value to remove: ")
                graph.remove_node(node_value)
                print(f"Node {node_value} removed successfully.")

            elif choice == '6':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                node1 = input("Enter the first node of the edge to remove: ")
                node2 = input("Enter the second node of the edge to remove: ")
                try:
                    graph.remove_edge(node1, node2)
                    print(f"Edge between {node1} and {node2} removed successfully.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == '7':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                filename = input("Enter the filename to save the graph to: ")
                try:
                    graph.save_to_file(filename)
                    print(f"Graph saved successfully to '{filename}'.")
                except IOError as e:
                    print(f"Error: {e}")

            elif choice == '8':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                edges = graph.get_edges()
                if edges:
                    print("Edges in the graph:")
                    for edge in edges:
                        print(edge)
                else:
                    print("No edges in the graph.")

            elif choice == '9':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                node_value = input("Enter the node value to see outgoing neighbors: ")
                outgoing_neighbors = graph.get_outgoing_neighbors(node_value)
                print(f"Outgoing neighbors for node {node_value}: {', '.join(map(str, outgoing_neighbors))}")

            elif choice == '10':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                node_value = input("Enter the node value to find non-adjacent nodes: ")
                non_adjacent_nodes = graph.get_non_adjacent_nodes(node_value)
                if non_adjacent_nodes:
                    print(f"Non-adjacent nodes for {node_value}: {', '.join(map(str, non_adjacent_nodes))}")
                else:
                    print(f"All nodes are adjacent to {node_value}.")

            elif choice == '11':
                if graph is None:
                    print("Please load or create a graph first.")
                    continue
                new_graph = graph.remove_edges_between_same_degree_nodes()
                print("New graph without edges between nodes of the same degree:")
                for edge in new_graph.get_edges():
                    print(edge)
                save_choice = get_confirmation("Do you want to save the new graph to a file?")
                if save_choice:
                    filename = input("Enter the filename to save the graph: ")
                    new_graph.save_to_file(filename)
                    print(f"Graph saved to {filename}")
            elif choice == "12":
                try:
                    components = graph.is_tree_or_forest_bfs()
                    if components == 1:
                        print("The graph is a tree.")
                    else:
                        print("The graph is a forest.")
                except ValueError as e:
                    print(f"Error: {e}")
            elif choice == '13':
                try:
                    u = input("Enter the first node (u): ")
                    v = input("Enter the second node (v): ")
                    result = graph.find_common_nodes_same_distance_dfs(u, v)
                    print(f"Nodes with paths from both {u} and {v} of equal length: {result}")


                except Exception as e:
                    print(f"An error occurred: {e}")
            elif choice == "14":
                if graph is None:
                    print("No graph loaded. Please load or create a graph first.")
                else:
                    try:
                        mst_edges, total_weight = graph.prim_mst()
                        print("Minimum Spanning Tree edges:")
                        for edge in mst_edges:
                            print(f"({edge[0]}, {edge[1]}) weight: {edge[2]}")
                        print(f"Total weight of the MST: {total_weight}")

                        save_choice = input("Would you like to save the MST to a file? (y/n): ").strip().lower()
                        if save_choice == 'y':
                            filename = input("Enter the filename to save the MST: ").strip()
                            with open(filename, 'w') as file:
                                file.write('False\nTrue\n')
                                for edge in mst_edges:
                                    file.write(f"{edge[0]} {edge[1]} {edge[2]}\n")
                            print(f"MST has been saved to {filename}")
                    except ValueError as e:
                        print(f"Error: {str(e)}")
            elif choice == "15":
                try:
                    u = input("Enter the start node: ")
                    distances, path_counts, paths = graph.dijkstra(u)
                    print(f"Distances from {u}: {distances}")
                    print(f"Number of shortest paths: {path_counts}")
                    print("Shortest paths:")
                    for node, node_paths in paths.items():
                        print(f"To {node} - {len(node_paths)}: {node_paths}")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "16":
                try:
                    u = input("Enter the start node: ")
                    v = input("Enter the end node: ")
                    k = int(input("Enter the number of shortest paths to find (k): "))
                    paths = graph.bellman_ford(u, v, k)

                    print(f"{k} shortest paths from {u} to {v}:")
                    for distance, path in paths:
                        print(f"Path: {path}, Distance: {distance}")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "17":
                try:
                    pairs = graph.floyd_warshall()
                    if pairs:
                        print("Pairs of nodes with paths of arbitrarily small length:")
                        for pair in pairs:
                            print(f"{pair[0]} - {pair[1]}")
                    else:
                        print("No such pairs exist.")
                except ValueError as e:
                    print(f"Error: {e}")
            elif choice == "18":
                try:
                    source = input("Enter the source: ").strip()
                    sink = input("Enter the sink: ").strip()
                    max_flow, flow = graph.edmonds_karp(source, sink)
                    print(f"Максимальный поток из '{source}' в '{sink}'= {max_flow}")
                    print("Flow distribution:")
                    for u in flow:
                        for v, f in flow[u].items():
                            if f > 0:
                                print(f"  {u} -> {v}: {f}")
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("Invalid choice. Please select a valid option.")

        except Exception as e:
            print(f"Error: {e}. Please try again.")

if __name__ == "__main__":
    main()