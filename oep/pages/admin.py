from django.contrib import admin
from .models import Podcast, Event, Toolkit


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'url']
    list_editable = ['url']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'time', 'location']


@admin.register(Toolkit)
class ToolkitAdmin(admin.ModelAdmin):
    list_display = ['title']
