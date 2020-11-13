from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from .models import Post, BlogPost, Insight, InsightOutput, ExternalPost, Category, Tag, Document


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
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


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file']
    list_editable = ['file']


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
    list_display = ['title', 'publish', 'added', 'view_count']
    list_editable = ['publish']
    search_fields = ['title']
    autocomplete_fields = [
        #'related_posts',
        'tags'
    ]
    readonly_fields = ['created_by', 'edited_by']
    inlines = [InsightOutputInline]


@admin.register(ExternalPost)
class ExternalPostAdmin(admin.ModelAdmin):
    list_display = ['description', 'url']
