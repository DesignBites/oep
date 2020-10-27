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


def graph(request):
    return render(request, 'network/graph.html', {
        'relation_groups': RELATION_GROUPS,
        'relation_type_palette': {rt.id: rt.color for rt in RelationType.objects.all()},
        'add_node_form': EntityForm(),
    })


def add_node(request):
    form = EntityForm()
