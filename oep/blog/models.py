from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.core import blocks
from wagtailcolumnblocks.blocks import ColumnsBlock


class BlogPage(Page):
    photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Background photo',
    )
    header = RichTextField(_('Header (English)'), max_length=500)
    header_fi = RichTextField(_('Header (Finnish)'), max_length=500, blank=True, null=True)
    text = RichTextField(_('Text (English)'))
    text_fi = RichTextField(_('Text (Finnish)'), blank=True, null=True)

    max_count = 1

    content_panels = Page.content_panels + [
        ImageChooserPanel('photo'),
        FieldPanel('header'),
        FieldPanel('header_fi'),
        FieldPanel('text'),
        FieldPanel('text_fi'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context.update({
            'categories': BlogCategory.objects.all(),
            'instagram_posts': InstagramPost.objects.all(),
        })
        return context


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPostPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


@register_snippet
class BlogCategory(ClusterableModel):
    name = models.CharField(_('Name (English)'), max_length=255)
    name_fi = models.CharField(_('Name (Finnish)'), max_length=255, blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=1)

    panels = [
        FieldPanel('name'),
        FieldPanel('name_fi'),
        FieldPanel('order'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _('blog categories')
        ordering = ('order',)


@register_snippet
class DefaultThumbnail(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image', null=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    panels = [
        ImageChooserPanel('image'),
    ]

    def __str__(self):
        return str(self.image)


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


class BlogPostPage(Page):
    body = StreamField([
        ('heading', blocks.RichTextBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', blocks.StructBlock([
            ('quote', blocks.RichTextBlock()),
            ('source', blocks.CharBlock(required=False))
        ])),
        ('columns', ColumnBlocks(form_classname="full")),
    ], verbose_name=_('Body (English)'))
    body_fi = StreamField([
        ('heading', blocks.RichTextBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', blocks.StructBlock([
            ('quote', blocks.RichTextBlock()),
            ('source', blocks.CharBlock(required=False))
        ])),
        ('columns', ColumnBlocks(form_classname="full")),
    ], blank=True, null=True, verbose_name=_('Body (Finnish)'))

    category = ParentalKey('blog.BlogCategory', blank=True, null=True, on_delete=models.SET_NULL)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    date = models.DateField("Post date", default=timezone.now)
    author = models.CharField(max_length=100, blank=True, null=True)
    photo_credits = models.CharField(max_length=100, blank=True, null=True)
    cover_photo = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    thumbnail = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    excerpt = RichTextField(_('Excerpt (English)'), blank=True, help_text=_('Please aim for approximately 200 characters.'))
    excerpt_fi = RichTextField(_('Excerpt (Finnish)'), blank=True)

    related_pages = StreamField([
        ('page', blocks.PageChooserBlock()),
    ], blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('body_fi'),
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('photo_credits'),
            FieldPanel('date'),
            FieldPanel('category'),
            FieldPanel('tags'),
        ], heading=_("Post information")),
        MultiFieldPanel([
            ImageChooserPanel('cover_photo'),
            FieldPanel('excerpt'),
            FieldPanel('excerpt_fi'),
            ImageChooserPanel('thumbnail'),
        ], heading=_("Meta info")),
        StreamFieldPanel('related_pages'),
    ]

    def get_title(self):
        for block in self.body:
            if block.block_type == 'heading':
                return block.value
        return self.title

    def get_thumbnail(self):
        if not self.thumbnail:
            thumbnail = DefaultThumbnail.objects.order_by('?').first()
            return thumbnail and thumbnail.image
        return self.thumbnail

    def get_category(self):
        return self.category


class BlogTagIndexPage(Page):
    max_count = 1

    def get_context(self, request):
        tag = request.GET.get('tag')
        posts = BlogPostPage.objects.filter(tags__name=tag)

        context = super().get_context(request)
        context['posts'] = posts
        return context


@register_snippet
class InstagramPost(models.Model):
    url = models.URLField('Instagram post URL')

    panels = [
        FieldPanel('url'),
    ]

    def __str__(self):
        return self.url
