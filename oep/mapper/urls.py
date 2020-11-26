from django.urls import path
from .views import index, connections_save, grid_save, upload_map, page_view, \
    ring_view, venn_view, suggest_view, node_add, node_update, node_delete, map_extend, approve_terms, map_save


urlpatterns = [
    path('upload/', upload_map, name='mapper_upload'),
    path('grid/', grid_save, name='mapper_grid_save'),
    path('connections/', connections_save, name='mapper_connections_save'),

    path('view/ring/', ring_view, name='mapper_ring'),
    path('view/venn/', venn_view, name='mapper_venn'),
    path('view/suggest/', suggest_view, name='mapper_suggest'),

    path('map/add/', node_add, name='mapper_add'),
    path('map/extend/', map_extend, name='mapper_extend'),

    path('terms/ok/', approve_terms, name='mapper_approve_terms'),
    path('save/', map_save, name='mapper_save'),
    path('update/', node_update, name='mapper_node_update'),
    path('delete/', node_delete, name='mapper_node_delete'),

    path('<int:page_no>/', page_view, name='mapper_page'),
    path('<slug:workshop_slug>/<int:page_no>/', page_view, name='mapper_page_workshop'),

    path('', index, name='mapper_index'),
    path('<slug:workshop_slug>/', index, name='mapper_index_workshop'),
]
