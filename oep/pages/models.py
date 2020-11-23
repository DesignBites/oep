from django.db import models
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks
from django.utils.html import escape
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler


class NewWindowExternalLinkHandler(LinkHandler):
    # This specifies to do this override for external links only.
    # Other identifiers are available for other types of links.
    identifier = 'external'

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        # Let's add the target attr, and also rel="noopener" + noreferrer fallback.
        # See https://github.com/whatwg/html/issues/4078.
        return '<a href="%s" target="_blank" rel="noopener noreferrer">' % escape(href)


@hooks.register('register_rich_text_features')
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)


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
    footer = RichTextField(blank=True, null=True)

    max_count = 1

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            ImageChooserPanel('photo'),
            FieldPanel('header'),
            FieldPanel('text'),
        ]),
        StreamFieldPanel('team_members'),
        FieldPanel('footer'),
    ]


class PodcastsPage(Page):
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(max_length=500)
    text = RichTextField()
    podcasts = StreamField([
        ('podcast', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('thumbnail', ImageChooserBlock(required=False)),
            ('description', blocks.RichTextBlock(required=False)),
            ('url', blocks.URLBlock(required=False)),
        ]))
    ], blank=True)

    max_count = 1

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            ImageChooserPanel('photo'),
            FieldPanel('header'),
            FieldPanel('text'),
        ]),
        StreamFieldPanel('podcasts'),
    ]
