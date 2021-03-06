from django.urls import path
from .views import index, connections_save, grid_save, upload_map, page_view, add_custom_similarity, \
    ring_view, venn_view, suggest_view, node_update, node_delete, approve_terms


urlpatterns = [
    path('terms/', approve_terms, name='mapper_terms'),
    path('upload/', upload_map, name='mapper_upload'),
    path('grid/', grid_save, name='mapper_grid_save'),
    path('connections/', connections_save, name='mapper_connections_save'),

    path('view/circles/', ring_view, name='mapper_ring'),
    path('view/venn/', venn_view, name='mapper_venn'),
    path('view/suggestions/', suggest_view, name='mapper_suggest'),

#    path('view/param/', add_custom_similarity, name='mapper_add_parameter'),

    path('update/', node_update, name='mapper_node_update'),
    path('delete/', node_delete, name='mapper_node_delete'),

    path('<int:page_no>/', page_view, name='mapper_page'),
    path('<slug:workshop_slug>/<int:page_no>/', page_view, name='mapper_page_workshop'),

    path('', index, name='mapper_index'),
    path('<slug:workshop_slug>/', index, name='mapper_index_workshop'),
]
