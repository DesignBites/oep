from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import translate_url
from django.utils import timezone
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from oep.blog.models import Post


@cache_page(5*60)  # 5 mins
def index(request):
    posts = Post.objects.filter(
        publish=True,
        publish_at__lt=timezone.now(),
    )
    return render(request, 'index.html', {
        'recent_posts': posts[:6],
        'featured_posts': posts.filter(featured=True)[:6],
    })


def set_language(request):
    next_page = request.META.get('HTTP_REFERER')
    response = HttpResponseRedirect(next_page) if next_page else HttpResponseRedirect('/')
    lang_code = request.GET.get('lang')
    next_trans = translate_url(next_page, lang_code)
    if next_trans != next_page:
        response = HttpResponseRedirect(next_trans)
    if hasattr(request, 'session'):
        request.session[LANGUAGE_SESSION_KEY] = lang_code
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME, lang_code,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
    )
    return response
