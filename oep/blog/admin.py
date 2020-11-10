from django.contrib import admin
from .models import Post, Category, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'category', 'publish', 'added', 'view_count']
    list_editable = ['type', 'category', 'publish']
    prepopulated_fields = {"slug": ('title',)}
    search_fields = ['title']
    autocomplete_fields = ['related_posts', 'tags']

    def save_model(self, request, obj, form, change):
        obj.edited_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']
    search_fields = ['name']

    def post_count(self, obj):
        return obj.post_set.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']
    search_fields = ['name']

    def post_count(self, obj):
        return obj.post_set.count()


