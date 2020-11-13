from django.contrib import admin
from .models import Post, BlogPost, Insight, InsightOutput, ExternalPost, Category, Tag


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


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'publish', 'added', 'view_count']
    list_editable = ['category', 'publish']
    prepopulated_fields = {"slug": ('title',)}
    search_fields = ['title']
    autocomplete_fields = [
        #'related_posts',
        'tags'
    ]
    readonly_fields = ['created_by', 'edited_by']

    def save_model(self, request, obj, form, change):
        obj.edited_by = request.user
        super().save_model(request, obj, form, change)


class InsightOutputInline(admin.StackedInline):
    model = InsightOutput


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'image', 'url', 'tags', 'publish', 'pinned', 'created_by', 'edited_by']
    list_display = ['title', 'publish', 'added', 'view_count']
    list_editable = ['publish']
    search_fields = ['title']
    autocomplete_fields = ['tags']
    readonly_fields = ['created_by', 'edited_by']
    inlines = [InsightOutputInline]


@admin.register(ExternalPost)
class ExternalPostAdmin(admin.ModelAdmin):
    fields = ['image', 'description', 'url', 'tags', 'publish', 'pinned', 'created_by', 'edited_by']
    list_display = ['description', 'url']
    search_fields = ['description']
    autocomplete_fields = ['tags']
