from django.urls import path
from .views import index, graph_create, graph_update, grid_save, graph_upload, view_page


urlpatterns = [
    path('create/', graph_create, name='graph_create'),
    path('update/', graph_update, name='graph_update'),
    path('upload/', graph_upload, name='graph_upload'),
    path('grid/', grid_save, name='mapper_grid_save'),

    path('<int:page_no>/', view_page, name='page_detail'),
    path('<slug:workshop_slug>/<int:page_no>/', view_page, name='page_detail_workshop'),

    path('', index, name='mapper_index'),
    path('<slug:workshop_slug>/', index, name='mapper_index_workshop'),
]
