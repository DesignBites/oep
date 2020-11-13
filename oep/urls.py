from django.contrib import admin
from django.urls import path, include
from django.utils.translation import ugettext as _
from django.conf import settings
from django.conf.urls.static import static
from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from .views import set_language


urlpatterns = [
    path('admin/', admin.site.urls),
    path('lang/', set_language, name='set_lang'),

    path('mapper/', include('oep.mapper.urls')),

    path('wagtail/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('posts/', include('oep.posts.urls')),

    path(r'', include(wagtail_urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.index_title = _('OEP')
admin.site.site_header = _('OEP Administration')
admin.site.site_title = _('OEP Management')
