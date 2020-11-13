from django.views.generic import TemplateView
from .models import TeamMemberProfile, Event, Toolkit, Podcast, Page


class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page': Page.objects.filter(name='home').first()
        })
        return context


class AboutView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'team': TeamMemberProfile.objects.all(),
            'page': Page.objects.filter(name='about').first()
        })
        return context


class EventsView(TemplateView):
    template_name = 'pages/events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'events': Event.objects.all(),
            'page': Page.objects.filter(name='events').first()
        })
        return context


class ToolsView(TemplateView):
    template_name = 'pages/tools.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'toolkits': Toolkit.objects.all(),
            'page': Page.objects.filter(name='tools').first()
        })
        return context


class PodcastsView(TemplateView):
    template_name = 'pages/podcasts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'podcasts': Podcast.objects.all(),
            'page': Page.objects.filter(name='podcasts').first()
        })
        return context


class PostsView(TemplateView):
    template_name = 'pages/posts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'posts': Podcast.objects.all(),
            'page': Page.objects.filter(name='posts').first()
        })
        return context
