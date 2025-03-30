from django.shortcuts import render, redirect
from django.contrib import messages
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from .graph import Graph
import json

# Глобальная переменная для хранения текущего графа
current_graph = None

def index(request):
    return render(request, 'graph_app/index.html')

def validate_edge_input(from_vertex, to_vertex, weight, is_weighted):
    """Проверяет корректность введенных данных для ребра."""
    errors = []
    
    try:
        from_vertex = int(from_vertex)
    except (ValueError, TypeError):
        errors.append("Начальная вершина должна быть целым числом")
        
    try:
        to_vertex = int(to_vertex)
    except (ValueError, TypeError):
        errors.append("Конечная вершина должна быть целым числом")

    if is_weighted:
        if not weight:
            errors.append("Для взвешенного графа необходимо указать вес ребра")
        else:
            try:
                weight = int(weight)
                if weight <= 0:
                    errors.append("Вес ребра должен быть положительным числом")
            except (ValueError, TypeError):
                errors.append("Вес ребра должен быть целым числом")
    elif weight:
        errors.append("Нельзя указывать вес ребра для невзвешенного графа")

    return errors

def visualize_graph(request):
    global current_graph
    if current_graph is None:
        # Создаем пустой граф при первом открытии
        current_graph = Graph(directed=True, weighted=True)

    # Отладочная печать
    print("Визуализация графа:")
    print("Вершины:", current_graph.nodes)
    print("Ребра:", current_graph.edges)

    # Конвертируем граф в NetworkX граф для визуализации
    G = nx.MultiDiGraph()
    
    # Добавляем вершины и ребра в NetworkX граф
    for node, node_type in current_graph.nodes.items():
        G.add_node(node, node_type=node_type)
    
    for edge in current_graph.edges:
        # Теперь edge содержит 4 элемента: from_vertex, to_vertex, cost, delivery_time
        G.add_edge(edge[0], edge[1], cost=edge[2], delivery_time=edge[3])

    # Создаем визуализацию
    plt.figure(figsize=(16, 12), dpi=100)
    
    # Улучшенное размещение вершин с несколькими стратегиями
    warehouse_nodes = [node for node, attr in G.nodes(data=True) if attr.get('node_type') == 'warehouse']
    client_nodes = [node for node, attr in G.nodes(data=True) if attr.get('node_type') == 'client']
    
    # Используем spring_layout с параметрами для лучшего разделения вершин
    pos = nx.spring_layout(G, k=4, iterations=50, seed=42)
    
    # Рисуем узлы разных типов разными цветами
    if warehouse_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=warehouse_nodes, node_color='lightblue', 
                             node_size=500, label='Склады')
    
    if client_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=client_nodes, node_color='lightgreen', 
                             node_size=500, label='Клиенты')
    
    # Рисуем веса рёбер
    if current_graph.weighted:
        # Добавляем метки стоимости
        edge_labels_cost = {(edge[0], edge[1]): f"{edge[2]} руб." for edge in current_graph.edges}
        nx.draw_networkx_edge_labels(G, pos, 
                                     edge_labels=edge_labels_cost, 
                                     label_pos=0.8,  
                                     font_size=6, 
                                     font_color='red',
                                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.5))
        
        # Добавляем метки времени доставки
        edge_labels_time = {(edge[0], edge[1]): f"{edge[3]} ч." for edge in current_graph.edges}
        nx.draw_networkx_edge_labels(G, pos, 
                                     edge_labels=edge_labels_time, 
                                     label_pos=0.2,  
                                     font_size=6, 
                                     font_color='blue',
                                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.5))
    
    # Рисуем рёбра с изогнутыми линиями для встречных направлений
    for u, v, data in G.edges(data=True):
        # Проверяем, есть ли обратное ребро
        if G.has_edge(v, u):
            # Рисуем изогнутые рёбра для встречных направлений
            nx.draw_networkx_edges(G, pos, 
                                   edgelist=[(u, v)], 
                                   edge_color='gray', 
                                   arrows=True, 
                                   arrowsize=20,
                                   connectionstyle=f'arc3,rad=0.2',  # Изгиб вправо
                                   width=1)
            nx.draw_networkx_edges(G, pos, 
                                   edgelist=[(v, u)], 
                                   edge_color='gray', 
                                   arrows=True, 
                                   arrowsize=20,
                                   connectionstyle=f'arc3,rad=-0.2',  # Изгиб влево
                                   width=1)
        else:
            # Для однонаправленных рёбер - обычная стрелка
            nx.draw_networkx_edges(G, pos, 
                                   edgelist=[(u, v)], 
                                   edge_color='gray', 
                                   arrows=True, 
                                   arrowsize=20,
                                   width=1)
    
    # Рисуем метки узлов
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")
    
    # Добавляем легенду
    plt.legend(loc='best', fontsize=12)
    
    # Проверяем, есть ли найденный путь для выделения
    if 'shortest_path' in request.session:
        path = request.session['shortest_path']
        print("Найденный путь:", path)  # Отладочная печать
        
        # Выделяем вершины найденного пути красным
        path_nodes = nx.draw_networkx_nodes(G, pos, 
                                            nodelist=path, 
                                            node_color='red', 
                                            node_size=600, 
                                            label='Путь')
        
        # Выделяем рёбра найденного пути красным
        path_edges = list(zip(path, path[1:]))
        print("Рёбра пути:", path_edges)  # Отладочная печать
        nx.draw_networkx_edges(G, pos, 
                               edgelist=path_edges, 
                               edge_color='red', 
                               arrows=True, 
                               arrowsize=25,
                               width=2)
    
    # Настраиваем отображение
    plt.axis('off')
    
    # Сохраняем график в память
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    
    # Кодируем изображение в base64
    graphic = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'graph_app/visualize.html', {
        'graphic': graphic,
        'current_graph': current_graph
    })

def add_vertex(request):
    global current_graph
    if request.method == 'POST' and current_graph is not None:
        try:
            vertex_name = request.POST.get('vertex_name')
            vertex_type = request.POST.get('vertex_type')
            
            if not vertex_name:
                messages.error(request, 'Необходимо указать значение вершины')
                return redirect('visualize_graph')
            
            if not vertex_type or vertex_type not in ['warehouse', 'client']:
                messages.error(request, 'Необходимо указать корректный тип вершины (склад или клиент)')
                return redirect('visualize_graph')
            
            current_graph.add_node(vertex_name, vertex_type)
            messages.success(request, f'Вершина {vertex_name} ({vertex_type}) успешно добавлена!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении вершины: {str(e)}')
    return redirect('visualize_graph')

def add_edge(request):
    global current_graph
    if request.method == 'POST' and current_graph is not None:
        try:
            from_vertex = request.POST.get('from_vertex')
            to_vertex = request.POST.get('to_vertex')
            cost = request.POST.get('cost')
            delivery_time = request.POST.get('delivery_time')
            
            if not from_vertex or not to_vertex:
                messages.error(request, 'Необходимо указать начальную и конечную вершины')
                return redirect('visualize_graph')
            
            try:
                cost = float(cost)
                delivery_time = float(delivery_time)
            except (ValueError, TypeError):
                messages.error(request, 'Стоимость и время доставки должны быть числами')
                return redirect('visualize_graph')
            
            current_graph.add_edge(from_vertex, to_vertex, cost, delivery_time)
            messages.success(request, f'Ребро от {from_vertex} к {to_vertex} добавлено: {cost} руб., {delivery_time} ч.')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении ребра: {str(e)}')
    return redirect('visualize_graph')

def delete_vertex(request):
    global current_graph
    if request.method == 'POST' and current_graph is not None:
        try:
            vertex_name = request.POST.get('vertex_name')
            
            if not vertex_name:
                messages.error(request, 'Необходимо указать значение вершины')
                return redirect('visualize_graph')
                
            if vertex_name not in current_graph.nodes:
                messages.error(request, f'Вершина {vertex_name} не существует')
                return redirect('visualize_graph')
                
            current_graph.remove_node(vertex_name)
            messages.success(request, f'Вершина {vertex_name} успешно удалена!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Ошибка при удалении вершины: {str(e)}')
    return redirect('visualize_graph')

def remove_edge(request):
    global current_graph
    if request.method == 'POST' and current_graph is not None:
        try:
            from_vertex = request.POST.get('from_vertex')
            to_vertex = request.POST.get('to_vertex')
            
            if not from_vertex or not to_vertex:
                messages.error(request, 'Необходимо указать начальную и конечную вершины')
                return redirect('visualize_graph')
            
            # Проверяем существование ребра
            edge_exists = any(edge[0] == from_vertex and edge[1] == to_vertex for edge in current_graph.edges)
            
            if not edge_exists:
                messages.error(request, f'Ребро от {from_vertex} к {to_vertex} не существует')
                return redirect('visualize_graph')
            
            # Удаляем ребро
            current_graph.edges = [edge for edge in current_graph.edges if not (edge[0] == from_vertex and edge[1] == to_vertex)]
            
            messages.success(request, f'Ребро {from_vertex} -> {to_vertex} успешно удалено!')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении ребра: {str(e)}')
    return redirect('visualize_graph')

def create_empty_graph(request):
    global current_graph
    current_graph = Graph(directed=True, weighted=True)
    messages.success(request, 'Создан новый пустой граф!')
    return redirect('visualize_graph')

def load_graph(request):
    global current_graph
    if request.method == 'POST' and 'graph_file' in request.FILES:
        try:
            # Читаем загруженный файл
            graph_file = request.FILES['graph_file']
            
            # Проверяем расширение файла
            if not graph_file.name.endswith('.json'):
                messages.error(request, 'Пожалуйста, загрузите JSON-файл')
                return redirect('visualize_graph')
            
            # Декодируем и парсим JSON
            file_content = graph_file.read().decode('utf-8')
            print("Содержимое файла:", file_content)  # Отладочная печать
            
            graph_data = json.loads(file_content)
            print("Распарсенные данные:", graph_data)  # Отладочная печать
            
            # Создаем новый граф
            current_graph = Graph(directed=True, weighted=True)
            
            # Добавляем вершины
            nodes = graph_data.get('nodes', {})
            print("Вершины для добавления:", nodes)  # Отладочная печать
            
            for node_name, node_type in nodes.items():
                print(f"Добавление вершины: {node_name}, тип: {node_type}")  # Отладочная печать
                current_graph.add_node(node_name, node_type)
            
            # Добавляем ребра
            edges = graph_data.get('edges', [])
            print("Ребра для добавления:", edges)  # Отладочная печать
            
            for edge in edges:
                from_vertex = edge.get('from')
                to_vertex = edge.get('to')
                cost = edge.get('cost', 0)
                delivery_time = edge.get('delivery_time', 0)
                
                print(f"Добавление ребра: {from_vertex} -> {to_vertex}, стоимость: {cost}, время: {delivery_time}")  # Отладочная печать
                current_graph.add_edge(from_vertex, to_vertex, cost, delivery_time)
            
            # Отладочная печать
            print("Загруженный граф:")
            print("Вершины:", current_graph.nodes)
            print("Ребра:", current_graph.edges)
            
            messages.success(request, 'Граф успешно загружен!')
        except json.JSONDecodeError as e:
            print("Ошибка декодирования JSON:", e)  # Отладочная печать
            messages.error(request, f'Ошибка при чтении JSON-файла: {e}')
        except ValueError as e:
            print("Ошибка значения:", e)  # Отладочная печать
            messages.error(request, str(e))
        except Exception as e:
            print("Неизвестная ошибка:", e)  # Отладочная печать
            messages.error(request, f'Ошибка при загрузке графа: {str(e)}')
    
    return redirect('visualize_graph')

def find_shortest_path(request):
    global current_graph
    if request.method == 'POST':
        try:
            start_vertex = request.POST.get('start_vertex')
            end_vertex = request.POST.get('end_vertex')
            path_type = request.POST.get('path_type', 'cost')

            if not start_vertex or not end_vertex:
                messages.error(request, 'Укажите начальную и конечную вершины')
                return redirect('visualize_graph')

            if path_type == 'optimal':
                path, total_cost, total_time = current_graph.find_optimal_path(start_vertex, end_vertex)
                message = (
                    f"📍 Оптимальный путь:\n"
                    f"   {' → '.join(path)}\n\n"
                    f"💰 Общая стоимость: {total_cost} руб.\n"
                    f"⏱️ Общее время доставки: {total_time} часов"
                )
            else:
                path, total_weight = current_graph.find_shortest_path(start_vertex, end_vertex, path_type)
                weight_name = 'стоимость' if path_type == 'cost' else 'время доставки'
                message = (
                    f"📍 Кратчайший путь по {weight_name}:\n"
                    f"   {' → '.join(path)}\n\n"
                    f"{'💰' if path_type == 'cost' else '⏱️'} Общая {weight_name}: {total_weight} {'руб.' if path_type == 'cost' else 'часов'}"
                )
            
            # Сохраняем путь в сессию для визуализации
            request.session['shortest_path'] = path
            request.session.modified = True  # Явно указываем, что сессия изменена
            
            messages.success(request, message)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Ошибка при поиске пути: {str(e)}')
    
    return redirect('visualize_graph')
