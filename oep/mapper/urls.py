from django.urls import path
from .views import index, graph_create, graph_save, connections_save, grid_save, graph_upload, view_page, \
    ring_view, venn_view, suggest_view, map_add, map_extend


urlpatterns = [
    path('create/', graph_create, name='graph_create'),
    path('update/', graph_save, name='mapper_graph_save'),
    path('upload/', graph_upload, name='graph_upload'),
    path('grid/', grid_save, name='mapper_grid_save'),
    path('connections/', connections_save, name='mapper_connections_save'),

    path('view/ring/', ring_view, name='mapper_ring'),
    path('view/venn/', venn_view, name='mapper_venn'),
    path('view/suggest/', suggest_view, name='mapper_suggest'),

    path('map/add/', map_add, name='mapper_add'),
    path('map/extend/', map_extend, name='mapper_extend'),

    path('<int:page_no>/', view_page, name='page_detail'),
    path('<slug:workshop_slug>/<int:page_no>/', view_page, name='page_detail_workshop'),

    path('', index, name='mapper_index'),
    path('<slug:workshop_slug>/', index, name='mapper_index_workshop'),
]
