from django.urls import path
from .views import post_detail, post_list, post_editor, post_save, image_upload


urlpatterns = [
    path('', post_list, name='blog_index'),
    path('category/<slug:category>/', post_list, name='blog_category_list'),
    path('tag/<slug:tag>/', post_list, name='blog_tag_list'),
    path('populer/', post_list, {'popular': True}, name='blog_popular_list'),

    path('editor/', post_editor, name='blog_post_add'),
    path('editor/<int:post_id>/', post_editor, name='blog_post_edit'),
    path('save/', post_save, name='blog_post_save'),
    path('upload/img/', image_upload, name='blog_post_upload_image'),

    path('<slug:slug>/', post_detail, name='blog_post_detail'),
]
