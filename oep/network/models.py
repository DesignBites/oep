from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


RELATION_GROUPS = (
    ('o', _('Organizational')),
    ('c', _('Creative')),
    ('s', _('Social')),
    ('p', _('Polarity')),
)

ORGANIZATION_SIZES = (
    (1, _('Less than 5 employees')),
    (5, _('5 - 9 employees')),
    (10, _('10 or more employees')),
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

    def __str__(self):
        return self.name
