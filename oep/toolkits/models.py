from django.db import models
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks


class ToolkitsPage(Page):
    cover_photo = models.ForeignKey(
        'wagtailimages.Image', null=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    max_count = 1

    content_panels = Page.content_panels + [
        ImageChooserPanel('cover_photo'),
    ]


class ToolkitPage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image', null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    header = RichTextField(max_length=500)
    text = RichTextField()
    tools = StreamField([
        ('tool', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('thumbnail', ImageChooserBlock()),
            ('description', blocks.RichTextBlock(required=False)),
            ('url', blocks.URLBlock(required=False)),
        ])),
        ('doc', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('thumbnail', ImageChooserBlock()),
            ('description', blocks.RichTextBlock(required=False)),
            ('file', DocumentChooserBlock(required=False)),
        ]))
    ])

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('header'),
            FieldPanel('text'),
            ImageChooserPanel('image'),
        ], heading="Toolkit information"),
        StreamFieldPanel('tools'),
    ]

    def get_title(self):
        return self.header

    def get_thumbnail(self):
        return self.image

    def get_category(self):
        return 'Toolkits'
