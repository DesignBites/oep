from django.contrib import admin
from .models import Post, Category, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'category', 'publish', 'added', 'view_count']
    list_editable = ['type', 'category', 'publish']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']

    def post_count(self, obj):
        return obj.post_set.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']

    def post_count(self, obj):
        return obj.post_set.count()


