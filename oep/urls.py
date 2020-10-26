from django.contrib import admin
from django.urls import path
from oep.network.views import graph


urlpatterns = [
    path('admin/', admin.site.urls),
    path('graph/', graph, name='graph'),
]
