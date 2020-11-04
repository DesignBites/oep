from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.functional import cached_property
from django.template.loader import render_to_string
from django.utils.timezone import now
from slugify import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField(default=0)

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
    type = models.PositiveSmallIntegerField(choices=(
        (1, 'Blog post'),
        (2, 'Insight'),
        (3, 'Manifestation'),
    ), default=1)
    content = models.JSONField(editable=False)
    category = models.ForeignKey('category', blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True)

    related_posts = models.ManyToManyField('self', blank=True)

    publish = models.BooleanField(default=False)
    publish_at = models.DateTimeField(default=now)
    published_by = models.ForeignKey(
        User,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='published_post',
    )

    featured = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)

    added = models.DateTimeField(default=now, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(**kwargs)
        if self.pinned:
            Post.objects.filter(pinned=True).exclude(id=self.id).update(pinned=False)

    def __str__(self):
        return self.title or '-'

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    @cached_property
    def rendered(self):
        rendered_doc = ''
        for block in self.data['blocks']:
            rendered_doc += render_to_string(f'blog/blocks/{block["type"]}.html', block["data"])
        return rendered_doc

    @cached_property
    def similar_posts(self):
        return self.related_posts.filter(publish=True)

    class Meta:
        ordering = ('-pinned', '-added',)
