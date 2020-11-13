from django.urls import path
from .views import HomeView, AboutView, EventsView, PodcastsView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('tools/', EventsView.as_view(), name='tools'),
    path('events/', EventsView.as_view(), name='events'),
    path('podcasts/', PodcastsView.as_view(), name='podcasts'),
]
