from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import BlogPostPage, InstagramPost


class BlogPostPageAdmin(ModelAdmin):
    model = BlogPostPage
    list_display = ['title', 'category', 'date']


#class InstagramPostPageAdmin(ModelAdmin):
#    model = InstagramPost


#modeladmin_register(InstagramPostPageAdmin)
modeladmin_register(BlogPostPageAdmin)
