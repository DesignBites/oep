from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.core import blocks
from wagtailcolumnblocks.blocks import ColumnsBlock


class EventsPage(Page):
    title_fi = models.CharField(_('Title (Finnish)'), max_length=200, blank=True, null=True)
    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel('title_fi'),
    ]

    def get_pinned_event(self):
        return EventPage.objects.filter(pinned=True).live().first()

    def get_upcoming_events(self):
        return EventPage.objects.filter(time__gt=timezone.now()).live()

    def get_past_events(self):
        return EventPage.objects.filter(time__lt=timezone.now()).live()


class CommonBlocks(blocks.StreamBlock):
    heading = blocks.CharBlock(label=_('Heading (English)'), group="Common", form_classname="full title")
    heading_fi = blocks.CharBlock(label=_('Heading (Finnish)'), group="Common", form_classname="full title", required=False)
    paragraph = blocks.RichTextBlock(label=_('Paragraph (English)'), group="Common")
    paragraph_fi = blocks.RichTextBlock(label=_('Paragraph (Finnish)'), group="Common", required=False)
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
    title_fi = models.CharField(_('Title (Finnish)'), max_length=200, blank=True, null=True)
    text = StreamField([
        ('heading', blocks.RichTextBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', blocks.BlockQuoteBlock()),
        ('columns', ColumnBlocks(form_classname="full")),
    ], verbose_name=_('Text (English)'))
    text_fi = StreamField([
        ('heading', blocks.RichTextBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', blocks.BlockQuoteBlock()),
        ('columns', ColumnBlocks(form_classname="full")),
    ], blank=True, null=True, verbose_name=_('Text (Finnish)'))
    time = models.DateTimeField()
    location = models.CharField(max_length=300)
    pinned = models.BooleanField(default=False)
    cover_photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    thumbnail = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    excerpt = RichTextField(_('Excerpt (English)'), blank=True)
    excerpt_fi = RichTextField(_('Excerpt (Finnish)'), blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('text'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('title_fi'),
        MultiFieldPanel([
            FieldPanel('time'),
            FieldPanel('location'),
            FieldPanel('pinned'),
        ], heading=_("Event information")),
        StreamFieldPanel('text'),
        StreamFieldPanel('text_fi'),
        MultiFieldPanel([
            ImageChooserPanel('cover_photo'),
            FieldPanel('excerpt'),
            FieldPanel('excerpt_fi'),
            ImageChooserPanel('thumbnail'),
        ], heading=_("Meta info")),
    ]

    def save(self, **kwargs):
        super().save(**kwargs)
        if self.pinned:
            EventPage.objects.exclude(id=self.id).update(pinned=False)

    def get_title(self):
        for block in self.text:
            if block.block_type == 'heading':
                return block.value
        return self.title

    def get_title_fi(self):
        for block in self.text_fi:
            if block.block_type == 'heading':
                return block.value
        return self.get_title()
