from django.db import models
from django.utils import timezone
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


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


@register_snippet
class BlogCategory(ClusterableModel):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


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


class BlogPage(Page):
    body = StreamField([
        ('common', CommonBlocks()),
        ('columns', ColumnBlocks()),
    ])
    category = ParentalKey('blog.BlogCategory', blank=True, null=True, on_delete=models.SET_NULL)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date", default=timezone.now)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('category'),
            FieldPanel('tags'),
        ], heading="Blog information"),
        InlinePanel('gallery_images', label="Gallery images"),
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context


@register_snippet
class Infographic(ClusterableModel):
    description = models.TextField()
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.description
