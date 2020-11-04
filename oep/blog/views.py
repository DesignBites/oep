from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.timezone import now
from .models import Post, Category, Tag


def post_list(request, **kwargs):
    context = {}
    qs = Post.objects.filter(
        publish=True,
        publish_at__lt=now(),
    )
    if kwargs.get('category'):
        qs = qs.filter(category__slug=kwargs.get('category'))
        category = get_object_or_404(Category, slug=kwargs['category'])
        context.update({
            'list_type': _('category'),
            'category': category,
            'title': category.name,
        })
    elif kwargs.get('tag'):
        qs = qs.filter(tags__slug=kwargs.get('tag'))
        tag = get_object_or_404(Tag, slug=kwargs['tag'])
        context.update({
            'list_type': _('tag'),
            'tag': tag,
            'title': tag.name,
            'pages': Page.objects.filter(content__tags=tag),
        })
    elif kwargs.get('popular'):
        qs = qs.order_by('-view_count')[:20]
        context.update({
            'list_type': _('popular'),
            'title': _('popular'),
        })
    context.update({
        'post_list': qs.distinct(),
    })
    return render(request, 'blog/post_list.html', context)


@cache_page(5*60)  # 5 mins
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.view_count += 1
    post.save()
    return render(request, 'blog/post_detail.html', {
        'post': post,
    })
