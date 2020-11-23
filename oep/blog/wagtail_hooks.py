from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import BlogPostPage


class BlogPostPageAdmin(ModelAdmin):
    model = BlogPostPage
    list_display = ['title', 'category', 'date']


#modeladmin_register(BlogPostPageAdmin)
