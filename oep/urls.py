from django.contrib import admin
from django.urls import path, include
from django.utils.translation import ugettext as _
from .views import set_language


urlpatterns = [
    path('admin/', admin.site.urls),
    path('mapper/', include('oep.mapper.urls')),
    path('blog/', include('oep.blog.urls')),

    path('dil/', set_language, name='set_lang'),
]


admin.site.index_title = _('OEP')
admin.site.site_header = _('OEP Administration')
admin.site.site_title = _('OEP Management')
