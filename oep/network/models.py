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


class Sector(models.Model):
    name = models.CharField(max_length=100)


class Map(models.Model):
    name = models.CharField(max_length=100)
    is_own = models.BooleanField(default=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    size = models.PositiveSmallIntegerField(choices=ORGANIZATION_SIZES, default=3)
    purpose = models.ForeignKey(Purpose, blank=True, null=True, on_delete=models.SET_NULL)
    graph = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        reverse('graph_detail', kwargs={
            'id': self.id,
        })

    def get_nodes(self):
        return {
            1: 'aaa',
            2: 'bbb',
            3: 'ccc',
        }


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
