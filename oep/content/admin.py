from django.contrib import admin
from .models import TeamMemberProfile, Podcast, Event, Document, Toolkit, BlogPost, PageContent


@admin.register(TeamMemberProfile)
class TeamMemberProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo']
    list_editable = ['photo']


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'url']
    list_editable = ['url']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'time', 'location']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file']
    list_editable = ['file']


@admin.register(Toolkit)
class ToolkitAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'section']
