from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.functional import cached_property
from slugify import slugify


ORGANIZATION_SIZES = (
    (1, _('Less than 5 employees')),
    (2, _('5 - 9 employees')),
    (3, _('10 or more employees')),
)


class Purpose(models.Model):
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.description


class Sector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RelationType(models.Model):
    name = models.CharField(max_length=100)
    question = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True, default='#ccc')
    directional = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(blank=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.order:
            self.order = RelationType.objects.all().count() + 1
        super().save(kwargs)

    class Meta:
        ordering = ('order',)


class Workshop(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse('mapper_index_workshop', kwargs={
            'workshop_slug': self.slug
        })


class Map(models.Model):
    name = models.CharField(_('Name of the organization'), max_length=100)
    workshop = models.ForeignKey(Workshop, blank=True, null=True, on_delete=models.SET_NULL)
    is_own = models.BooleanField(
        _('This is my own organization'),
        default=True,
        help_text=_("Uncheck the box if you are mapping an other organization's network")
    )
    sector = models.ForeignKey(
        Sector, verbose_name=_('The sector of the organization'),
        on_delete=models.CASCADE,
    )
    size = models.PositiveSmallIntegerField(
        _('Size of the organization'),
        choices=ORGANIZATION_SIZES, default=3,
    )
    purpose = models.ForeignKey(
        Purpose, verbose_name=_('Your primary purpose of using this tool'),
        blank=True, null=True, on_delete=models.SET_NULL,
    )
    stakeholders = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('graph_view', kwargs={
            'map_id': self.id,
        })
