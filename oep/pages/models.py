from django.db import models
from django.urls import reverse


class Page(models.Model):
    name = models.SlugField(unique=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    heading = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='pages/', blank=True, null=True)

    def __str__(self):
        return self.name or '-'

    def get_absolute_url(self):
        return reverse(self.name)


class PageSection(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    heading = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='pages/', blank=True, null=True)
    link = models.ForeignKey(
        Page, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='linked_sections',
    )

    def __str__(self):
        return f'{self.page} - {self.id}'


class TeamMemberProfile(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Podcast(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title


class Toolkit(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
