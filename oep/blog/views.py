import json
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.db.utils import IntegrityError
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import DefaultStorage
from slugify import slugify
from .models import Post, Category, Tag, POST_TYPES


def post_list(request, **kwargs):
    context = {}
    qs = Post.objects.filter(
        publish=True,
        publish_at__lt=timezone.now(),
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
        'popular_posts': Post.objects.filter(publish=True).order_by('-view_count')[:6]
    })


@login_required
def post_editor(request, post_id=None):
    if post_id:
        post = Post.objects.filter(
            id=post_id,
        ).first()
    else:
        post = None
    return render(request, 'blog/editor.html', {
        'post': post,
        'categories': Category.objects.filter(active=True),
        'types': POST_TYPES,
    })


@login_required
def post_save(request):
    content = json.loads(request.POST.get('data', ''))
    if request.is_ajax:
        title, image = None, None
        for block in content['blocks']:
            if not title and block['type'] == 'header':
                title = block['data']['text']
            elif not image and block['type'] == 'image':
                #image = block['data']['file']['url']  # AWS
                image = block['data']['file']['url'][len(settings.MEDIA_URL):]
        publish = request.POST.get('publish') == 'true'
        if publish:
            if not title:
                return JsonResponse({
                    'error': _('No title provided'),
                })
            if not image:
                return JsonResponse({
                    'error': _('No image provided'),
                })
        post_type = request.POST.get('type')
        post_id = request.POST.get('id')
        if post_id:
            post = Post.objects.get(id=post_id)
            post.type = post_type
            post.title = title
            post.content = content
            post.image = image
            post.publish = publish
            post.save()
        else:
            try:
                post = Post.objects.create(
                    type=post_type,
                    title=title,
                    image=image,
                    content=content,
                    publish=publish,
                    created_by=request.user,
                )
            except IntegrityError:
                return JsonResponse({
                    'error': _('A post with the same title already exists'),
                })
        post.tags.clear()
        tag_names = [
            t.strip()
            for t in request.POST.get('tags', '').split(',')
            if t.strip()
        ]
        for tag_name in tag_names:
            tag, c = Tag.objects.get_or_create(
                slug=slugify(tag_name),
                defaults={
                    'name': tag_name,
                }
            )
            post.tags.add(tag)
        category_name = request.POST.get('category').strip()
        if category_name:
            category, c = Category.objects.get_or_create(
                slug=slugify(category_name),
                defaults={
                    'name': category_name,
                }
            )
            post.category = category
            post.save()
        return JsonResponse({
            'id': post.id,
            'url': post.get_absolute_url(),
        })


@csrf_exempt
@login_required
def image_upload(request):
    if request.method == 'POST':
        image = request.FILES['image']
        fs = DefaultStorage()
        now = timezone.now()
        image_path = f'{settings.MEDIA_ROOT}/posts/{now.year}/{now.month}/{now.day}/{image.name}'
        filename = fs.save(
            image_path,
            image
        )
        #uploaded_file_url = fs.url(filename)  # for AWS
        uploaded_file_url = f'{settings.MEDIA_URL}posts/{now.year}/{now.month}/{now.day}/{image.name}'
        print(uploaded_file_url)
        return JsonResponse({
            'success': 1,
            'file': {
                'url': uploaded_file_url,
            }
        })
    return JsonResponse({
        'success': 0,
    })
