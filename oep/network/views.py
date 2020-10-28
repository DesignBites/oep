from collections import defaultdict
from django.shortcuts import render
from django import forms
from django.utils.translation import ugettext as _
from oep.network.models import Map, RelationType, RELATION_GROUPS, ORGANIZATION_SIZES


def relation_type_choices():
    choices = []
    for group_code, group_name in RELATION_GROUPS:
        choices.append(
            (group_name, [(rt.id, rt.name) for rt in RelationType.objects.filter(group=group_code)])
        )
    return choices


def add_to_choices():
    choices = [(0, _('Yourself'))]
    return choices


class EntityForm(forms.Form):
    add_to = forms.ChoiceField(label=_('Relate to'), choices=add_to_choices)
    name = forms.CharField(label=_('Name of the entity'))
    size = forms.ChoiceField(label=_('Size of the entity'), choices=ORGANIZATION_SIZES)
    relation_type = forms.ChoiceField(choices=relation_type_choices)
    weight = forms.ChoiceField(label=_('We interact'), choices=(
        (3, _('Regularly')),
        (2, _('Sometimes')),
        (1, _('Rarely')),
    ))


class StakeholderForm(forms.Form):
    name = forms.CharField(label=_('Name of the stakeholder'))
    size = forms.ChoiceField(label=_('Size of the stakeholder'), choices=ORGANIZATION_SIZES)
    weight = forms.ChoiceField(label=_('We interact'), choices=(
        (3, _('Regularly')),
        (2, _('Sometimes')),
        (1, _('Rarely')),
    ))


def graph(request):
    relation_groups = dict(RELATION_GROUPS)
    relation_types_grouped = defaultdict(dict)
    relation_types_flat = {}
    for rt in RelationType.objects.all():
        relation_types_grouped[relation_groups[rt.group]][rt.id] = rt
        relation_types_flat[rt.id] = {
            'color': rt.color,
            'name': rt.name,
        }
    group_first_relation = []
    for group_name in relation_groups.values():
        relation_types = relation_types_grouped.get(group_name)
        if relation_types:
            group_first_relation.append((
                group_name,
                list(relation_types.keys())[0]
            ))
    return render(request, 'network/graph.html', {
        'relation_groups': relation_groups,
        'group_first_relation': group_first_relation,
        'relation_types_grouped': dict(relation_types_grouped),
        'relation_types_flat': relation_types_flat,
        'add_node_form': EntityForm(),
        'add_stakeholder_form': StakeholderForm(),
    })


def add_node(request):
    form = EntityForm()
