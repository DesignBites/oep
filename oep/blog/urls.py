from django.urls import path
from .views import post_detail, post_list


urlpatterns = [
    path('category/<slug:category>/', post_list, name='blog_category_list'),
    path('tag/<slug:tag>/', post_list, name='blog_tag_list'),
    path('populer/', post_list, {'popular': True}, name='blog_popular_list'),

    path('<slug:slug>/', post_detail, name='content_detail'),
]
