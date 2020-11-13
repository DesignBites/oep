from django.contrib import admin
from .models import TeamMemberProfile, Podcast, Event, Toolkit, Page, PageSection


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


@admin.register(Toolkit)
class ToolkitAdmin(admin.ModelAdmin):
    list_display = ['title']


class PageSectionInline(admin.StackedInline):
    model = PageSection
    fk_name = 'page'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'title']
    inlines = [PageSectionInline]
