from django.shortcuts import render
from django import forms
from oep.network.models import Map, RelationType, RELATION_GROUPS, ORGANIZATION_SIZES


class EntityForm(forms.Form):
    name = forms.CharField()
    size = forms.ChoiceField(choices=ORGANIZATION_SIZES)
    relation_type_choices = []
    relation_type = forms.ChoiceField(choices=relation_type_choices)


def graph(request):
    return render(request, 'network/graph.html', {
        'relation_groups': RELATION_GROUPS,
        'relation_type_palette': {rt.id: rt.color for rt in RelationType.objects.all()},
        'add_node_form': EntityForm(),
    })


def add_node(request):
    form = EntityForm()
