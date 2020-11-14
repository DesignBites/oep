from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks


class HomePage(Page):
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(max_length=500)
    text = RichTextField()
    sections = StreamField([
        ('section', blocks.StructBlock([
            ('heading', blocks.RichTextBlock(form_classname="full")),
            ('text', blocks.RichTextBlock()),
            ('image', ImageChooserBlock()),
            ('link', blocks.PageChooserBlock()),
            ('link_text', blocks.CharBlock(required=False)),
        ])),
    ], blank=True)

    max_count = 1

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            ImageChooserPanel('photo'),
            FieldPanel('header'),
            FieldPanel('text'),
        ]),
        StreamFieldPanel('sections'),
    ]


class AboutPage(Page):
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(max_length=500)
    text = RichTextField()
    team_members = StreamField([
        ('team_member', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock()),
            ('photo', ImageChooserBlock()),
            ('bio', blocks.RichTextBlock()),
            ('email', blocks.EmailBlock(required=False)),
            ('phone', blocks.CharBlock(required=False)),
        ])),
    ], blank=True)

    max_count = 1

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            ImageChooserPanel('photo'),
            FieldPanel('header'),
            FieldPanel('text'),
        ]),
        StreamFieldPanel('team_members'),
    ]


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
