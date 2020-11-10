import json
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.timezone import now
from slugify import slugify


POST_TYPES = (
    (1, 'Blog post'),
    (2, 'Insight'),
    (3, 'Manifestation'),
)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse('blog_category_list', kwargs={'category': self.slug})

    @cached_property
    def content(self):
        return self.post_set.filter(publish=True)

    class Meta:
        ordering = ('order',)
        verbose_name_plural = 'categories'


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse('blog_tag_list', kwargs={'tag': self.slug})


class Post(models.Model):
    type = models.PositiveSmallIntegerField(choices=POST_TYPES, default=1)

    title = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)

    content = models.JSONField(blank=True, null=True)
    category = models.ForeignKey('category', blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)

    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True)

    related_posts = models.ManyToManyField('self', blank=True)

    publish = models.BooleanField(default=False)
    publish_at = models.DateTimeField(default=now, blank=True)
    created_by = models.ForeignKey(
        User,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='created_post',
        editable=False,
    )
    edited_by = models.ForeignKey(
        User,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='edited_post',
        editable=False,
    )

    featured = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)

    added = models.DateTimeField(default=now, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)

    def save(self, **kwargs):
        if self.title and not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(**kwargs)
        if self.pinned:
            Post.objects.filter(pinned=True).exclude(id=self.id).update(pinned=False)

    def clean(self):
        if self.publish:
            if not self.title:
                raise ValidationError('Title is missing')
            if not self.image:
                raise ValidationError('Image is missing')

    def __str__(self):
        return self.title or '-'

    def get_absolute_url(self):
        if self.publish:
            return reverse('blog_post_detail', kwargs={'slug': self.slug})
        else:
            return reverse('blog_post_edit', kwargs={'post_id': self.id})

    @cached_property
    def content_js(self):
        return json.dumps(self.content)

    @cached_property
    def rendered(self):
        rendered_doc = ''
        for block in self.content['blocks']:
            rendered_doc += render_to_string(f'blog/blocks/{block["type"]}.html', block["data"])
        return rendered_doc

    @cached_property
    def similar_posts(self):
        return self.related_posts.filter(publish=True)

    class Meta:
        ordering = ('-pinned', '-added',)
