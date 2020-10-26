from django.contrib import admin
from django.urls import path
from django.utils.translation import ugettext as _
from oep.network.views import graph


urlpatterns = [
    path('admin/', admin.site.urls),
    path('graph/', graph, name='graph'),
    path('graph/<int:id>/', graph, name='graph_detail'),
]


admin.site.index_title = _('OEP')
admin.site.site_header = _('OEP Administration')
admin.site.site_title = _('OEP Management')
