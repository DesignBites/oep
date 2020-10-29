from django.contrib import admin
from django.urls import path, include
from django.utils.translation import ugettext as _


urlpatterns = [
    path('admin/', admin.site.urls),
    path('graph/', include('oep.network.urls')),
]


admin.site.index_title = _('OEP')
admin.site.site_header = _('OEP Administration')
admin.site.site_title = _('OEP Management')
