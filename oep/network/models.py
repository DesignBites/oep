from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.functional import cached_property


RELATION_GROUPS = (
    ('o', _('Organizational')),
    ('c', _('Creative')),
    ('s', _('Social')),
    ('p', _('Polarity')),
)

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


class Map(models.Model):
    name = models.CharField(_('Name of the organization'), max_length=100)
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
    graph = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('graph_view', kwargs={
            'map_id': self.id,
        })


class RelationType(models.Model):
    group = models.CharField(
        max_length=1,
        choices=RELATION_GROUPS,
    )
    name = models.CharField(max_length=100)
    question = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True, default='#ccc')
    directional = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(blank=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.order:
            self.order = RelationType.objects.filter(group=self.group).count() + 1
        super().save(kwargs)

    @cached_property
    def group_next(self):
        return RelationType.objects.filter(group=self.group).filter(order__gt=self.order).order_by('order').first()

    @cached_property
    def group_prev(self):
        return RelationType.objects.filter(group=self.group).filter(order__lt=self.order).order_by('-order').first()

    class Meta:
        ordering = ('group', 'order',)
        unique_together = (('group', 'order'),)
