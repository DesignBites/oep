from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.functional import cached_property
from slugify import slugify


ORGANIZATION_SIZES = (
    (1, _('< 20')),
    (2, _('20 - 200')),
    (3, _('> 200')),
)


class Sector(models.Model):
    """
    Holds the sectors based on the ILO list.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StakeholderType(models.Model):
    """
    Stores types of stakeholders and which batch they belong to.
    """
    name = models.CharField(max_length=100)
    batch_no = models.PositiveSmallIntegerField()
    question = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    order = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('batch_no', 'order',)
        verbose_name = 'question'
        verbose_name_plural = 'questions'


class Workshop(models.Model):
    """
    Stores a workshop name. :model:`mapper.Map` can be related to a workshop instance.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse('mapper_index_workshop', kwargs={
            'workshop_slug': self.slug
        })


class Map(models.Model):
    """
    Holds all the information regarding a stakeholder map created in one session.
    """
    name = models.CharField(_('Name of the organization'), max_length=100)
    workshop = models.ForeignKey(Workshop, blank=True, null=True, on_delete=models.SET_NULL)
    is_own = models.BooleanField(
        _('This is my own organization'),
        default=True,
        help_text=_("Uncheck the box if you are mapping another organization's network")
    )
    sector = models.ForeignKey(
        Sector, verbose_name=_('The sector of the organization'),
        on_delete=models.CASCADE,
    )
    size = models.PositiveSmallIntegerField(
        _('Size of the organization'),
        choices=ORGANIZATION_SIZES, default=3,
    )
    purpose = models.TextField(
        _('Your primary purpose of using this tool'),
        blank=True, null=True,
    )
    stakeholders = models.JSONField(blank=True, null=True)
    own_parameter = models.CharField(max_length=100, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PageInfo(models.Model):
    page = models.CharField('Page number or name', max_length=20, db_index=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.page)

    class Meta:
        ordering = ('page',)
