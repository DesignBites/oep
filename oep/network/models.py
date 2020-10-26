from django.db import models
from django.contrib.auth.models import User


class Map(models.Model):
    pass


class NodeType(models.Model):
    description = models.CharField(max_length=100)


class Node(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(
        NodeType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
    )


RELATION_GROUPS = (
    ('o', 'Organizational'),
    ('c', 'Creative'),
    ('s', 'Social'),
    ('p', 'Polarity'),
)


class RelationType(models.Model):
    description = models.CharField(max_length=100)
    group = models.CharField(
        max_length=1,
        choices=RELATION_GROUPS,
    )
    directional = models.BooleanField(default=True)


class Edge(models.Model):
    node_1 = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='edges_1')
    node_2 = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='edges_2')
    type = models.ForeignKey(
        RelationType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
    )
    weight = models.PositiveSmallIntegerField(default=1)
