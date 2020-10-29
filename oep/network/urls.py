from django.urls import path
from oep.network.views import graph, graph_create, graph_update, graph_view, graph_upload


urlpatterns = [
    path('', graph, name='graph'),
    path('create/', graph_create, name='graph_create'),
    path('update/', graph_update, name='graph_update'),
    path('<int:map_id>/', graph_view, name='graph_view'),
    path('upload/', graph_upload, name='graph_upload'),
]
