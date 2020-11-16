from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.core import blocks
from wagtailcolumnblocks.blocks import ColumnsBlock


class EventsPage(Page):
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(max_length=500)
    text = RichTextField()

    max_count = 1

    content_panels = Page.content_panels + [
        ImageChooserPanel('photo'),
        FieldPanel('header'),
        FieldPanel('text'),
    ]


class CommonBlocks(blocks.StreamBlock):
    heading = blocks.CharBlock(group="Common", form_classname="full title")
    paragraph = blocks.RichTextBlock(group="Common")
    image = ImageChooserBlock(group="Common")


class ColumnBlocks(blocks.StreamBlock):
    column_1_1 = ColumnsBlock(
        CommonBlocks(),
        ratios=(1, 1),
        group='Columns',
        template='blocks/columns.html',
    )
    column_2_1 = ColumnsBlock(
        CommonBlocks(),
        ratios=(2, 1),
        group='Columns',
        template='blocks/columns.html',
    )
    column_1_2 = ColumnsBlock(
        CommonBlocks(),
        ratios=(1, 2),
        group='Columns',
        template='blocks/columns.html',
    )
    column_1_1_1 = ColumnsBlock(
        CommonBlocks(),
        ratios=(1, 1, 1),
        group='Columns',
        template='blocks/columns.html',
    )


class EventPage(Page):
    text = StreamField([
        ('heading', blocks.RichTextBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', blocks.BlockQuoteBlock()),
        ('columns', ColumnBlocks(form_classname="full")),
    ])
    time = models.DateTimeField()
    location = models.CharField(max_length=100, blank=True, null=True)
    cover_photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    thumbnail = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    excerpt = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('text'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('time'),
            FieldPanel('location'),
        ], heading="Event information"),
        StreamFieldPanel('text'),
        MultiFieldPanel([
            ImageChooserPanel('cover_photo'),
            FieldPanel('excerpt'),
            ImageChooserPanel('thumbnail'),
        ], heading="Meta info"),
    ]

    def get_title(self):
        for block in self.body:
            if block.block_type == 'heading':
                return block.value
        return self.title
