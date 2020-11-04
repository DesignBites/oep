from django.urls import path
from django.views.generic import TemplateView
from .views import index, graph_create, graph_update, graph_view, graph_upload, view_page


urlpatterns = [
    path('create/', graph_create, name='graph_create'),
    path('update/', graph_update, name='graph_update'),
    path('map/<int:map_id>/', graph_view, name='graph_view'),
    path('upload/', graph_upload, name='graph_upload'),

    path('<int:page_no>/', view_page, name='page_detail'),
    path('<slug:workshop_slug>/<int:page_no>/', view_page, name='page_detail_workshop'),

    path('', index, name='mapper_index'),
    path('<slug:workshop_slug>/', index, name='mapper_index_workshop'),
]
