from django.urls import path
from . import views

urlpatterns = [
    path('', views.visualize_graph, name='visualize_graph'),
    path('add_vertex/', views.add_vertex, name='add_vertex'),
    path('delete_vertex/', views.delete_vertex, name='delete_vertex'),
    path('add_edge/', views.add_edge, name='add_edge'),
    path('remove_edge/', views.remove_edge, name='remove_edge'),
    path('load_graph/', views.load_graph, name='load_graph'),
    path('create_empty_graph/', views.create_empty_graph, name='create_empty_graph'),
    path('find_shortest_path/', views.find_shortest_path, name='find_shortest_path'),
]
