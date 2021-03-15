from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks
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
    title_fi = models.CharField(_('Title (Finnish)'), max_length=200, blank=True, null=True)
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(_('Header (English)'), max_length=500)
    header_fi = RichTextField(_('Header (Finnish)'), max_length=500, blank=True, null=True)
    text = RichTextField(_('Text (English)'))
    text_fi = RichTextField(_('Text (Finnish)'), blank=True, null=True)
    sections = StreamField([
        ('section', blocks.StructBlock([
            ('heading', blocks.RichTextBlock(form_classname="full")),
            ('heading_fi', blocks.RichTextBlock(form_classname="full", required=False)),
            ('text', blocks.RichTextBlock(label=_('Text (English)'))),
            ('text_fi', blocks.RichTextBlock(label=_('Text (Finnish)'), required=False)),
            ('image', ImageChooserBlock()),
            ('link', blocks.PageChooserBlock()),
            ('link_text', blocks.CharBlock(label=_('Link text (English)'), required=False)),
            ('link_text_fi', blocks.CharBlock(label=_('Link text (Finnish)'), required=False)),
        ])),
    ], blank=True)

    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel('title_fi'),
        MultiFieldPanel([
            ImageChooserPanel('photo'),
            FieldPanel('header'),
            FieldPanel('header_fi'),
            FieldPanel('text'),
            FieldPanel('text_fi'),
        ]),
        StreamFieldPanel('sections'),
    ]


class AboutPage(Page):
    title_fi = models.CharField(_('Title (Finnish)'), max_length=200, blank=True, null=True)
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(_('Header (English)'), max_length=500)
    header_fi = RichTextField(_('Header (Finnish)'), max_length=500, blank=True, null=True)
    text = RichTextField(_('Text (English)'))
    text_fi = RichTextField(_('Text (Finnish)'), blank=True, null=True)
    team_members = StreamField([
        ('team_member', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock(label=_('Title (English)'))),
            ('title_fi', blocks.CharBlock(label=_('Title (Finnish)'), required=False)),
            ('photo', ImageChooserBlock()),
            ('bio', blocks.RichTextBlock(label=_('Bio (English)'))),
            ('bio_fi', blocks.RichTextBlock(label=_('Bio (Finnish)'), required=False)),
            ('email', blocks.EmailBlock(required=False)),
            ('phone', blocks.CharBlock(required=False)),
        ])),
    ], blank=True)
    footer = RichTextField(_('Footer (English)'), blank=True, null=True)
    footer_fi = RichTextField(_('Footer (Finnish)'), blank=True, null=True)

    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel('title_fi'),
        MultiFieldPanel([
            ImageChooserPanel('photo'),
            FieldPanel('header'),
            FieldPanel('header_fi'),
            FieldPanel('text'),
            FieldPanel('text_fi'),
        ]),
        StreamFieldPanel('team_members'),
        FieldPanel('footer'),
        FieldPanel('footer_fi'),
    ]


class PodcastsPage(Page):
    title_fi = models.CharField(_('Title (Finnish)'), max_length=200, blank=True, null=True)
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(_('Header (English)'), max_length=500)
    header_fi = RichTextField(_('Header (Finnish)'), max_length=500, blank=True, null=True)
    text = RichTextField(_('Text (English)'))
    text_fi = RichTextField(_('Text (Finnish)'), blank=True, null=True)
    podcasts = StreamField([
        ('podcast', blocks.StructBlock([
            ('title', blocks.CharBlock(label=_('Title (English)'))),
            ('title_fi', blocks.CharBlock(label=_('Title (Finnish)'), required=False)),
            ('thumbnail', ImageChooserBlock(required=False)),
            ('description', blocks.RichTextBlock(label=_('Description (English'), required=False)),
            ('description_fi', blocks.RichTextBlock(label=_('Description (Finnish)'), required=False)),
            ('url', blocks.URLBlock(required=False)),
        ]))
    ], blank=True)

    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel('title_fi'),
        MultiFieldPanel([
            ImageChooserPanel('photo'),
            FieldPanel('header'),
            FieldPanel('header_fi'),
            FieldPanel('text'),
            FieldPanel('text_fi'),
        ]),
        StreamFieldPanel('podcasts'),
    ]
