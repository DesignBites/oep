from django.db import models
from django.utils.translation import ugettext_lazy as _
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks


class ToolkitsPage(Page):
    title_fi = models.CharField(_('Title (Finnish)'), max_length=200, blank=True, null=True)
    cover_photo = models.ForeignKey(
        'wagtailimages.Image', null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    header = RichTextField(_('Header (English)'), max_length=500)
    header_fi = RichTextField(_('Header (Finnish)'), max_length=500, blank=True, null=True)
    text = RichTextField(_('Text (English)'))
    text_fi = RichTextField(_('Text (Finnish)'), blank=True, null=True)

    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel('title_fi'),
        ImageChooserPanel('cover_photo'),
        FieldPanel('header'),
        FieldPanel('header_fi'),
        FieldPanel('text'),
        FieldPanel('text_fi'),
    ]


class ToolkitPage(Page):
    title_fi = models.CharField(_('Title (Finnish)'), max_length=200, blank=True, null=True)
    header = RichTextField(_('Header (English)'), max_length=500)
    header_fi = RichTextField(_('Header (Finnish)'), max_length=500, blank=True, null=True)
    excerpt = RichTextField(
        _('Excerpt'),
        null=True,
        help_text='This text will appear on the toolkits index page.'
    )
    excerpt_fi = RichTextField(
        _('Excerpt (Finnish)'),
        null=True,
        help_text=_('This text will appear on the toolkits index page.'),
    )
    text = RichTextField(_('Text (English)'))
    text_fi = RichTextField(_('Text (Finnish)'), blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image', null=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text='This image will appear on the toolkits index page.'
    )
    background_image = models.ForeignKey(
        'wagtailimages.Image', null=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text="This is the background image of the toolkit's detail page."
    )
    tools = StreamField([
        ('tool', blocks.StructBlock([
            ('title', blocks.CharBlock(label=_('Title (English)'))),
            ('title_fi', blocks.CharBlock(label=_('Title (English)'), required=False)),
            ('thumbnail', ImageChooserBlock()),
            ('description', blocks.RichTextBlock(label=_('Description (English)'), required=False)),
            ('description_fi', blocks.RichTextBlock(label=_('Description (Finnish)'), required=False)),
            ('url', blocks.URLBlock(required=False)),
        ])),
        ('doc', blocks.StructBlock([
            ('title', blocks.CharBlock(label=_('Title (English)'))),
            ('title_fi', blocks.CharBlock(label=_('Title (English)'), required=False)),
            ('thumbnail', ImageChooserBlock()),
            ('description', blocks.RichTextBlock(label=_('Description (English)'), required=False)),
            ('description_fi', blocks.RichTextBlock(label=_('Description (Finnish)'), required=False)),
            ('file', DocumentChooserBlock(required=False)),
        ]))
    ])

    content_panels = Page.content_panels + [
        FieldPanel('title_fi'),
        MultiFieldPanel([
            FieldPanel('header'),
            FieldPanel('header_fi'),
            FieldPanel('excerpt'),
            FieldPanel('excerpt_fi'),
            FieldPanel('text'),
            FieldPanel('text_fi'),
            ImageChooserPanel('image'),
            ImageChooserPanel('background_image'),
        ], heading="Toolkit information"),
        StreamFieldPanel('tools'),
    ]

    def get_title(self):
        return self.header

    def get_thumbnail(self):
        return self.image

    def get_category(self):
        return 'Toolkits'
