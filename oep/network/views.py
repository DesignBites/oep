import json
from collections import defaultdict
from django.shortcuts import render
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from oep.network.models import Map, RelationType, RELATION_GROUPS, ORGANIZATION_SIZES


def relation_type_choices():
    choices = []
    for group_code, group_name in RELATION_GROUPS:
        choices.append(
            (group_name, [(rt.id, rt.name) for rt in RelationType.objects.filter(group=group_code)])
        )
    return choices


class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ['name', 'is_own', 'sector', 'size', 'purpose']


class MapUploadForm(forms.Form):
    graph = forms.FileField(
        label=_('Map file'),
        help_text=_('Please select and upload the exported JSON map file.'),
    )


class EntityForm(forms.Form):
    add_to = forms.ChoiceField(label=_('Relate to'), choices=[])
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
    """
    size = forms.ChoiceField(label=_('Size of the stakeholder'), choices=ORGANIZATION_SIZES)
    weight = forms.ChoiceField(label=_('We interact'), choices=(
        (3, _('Regularly')),
        (2, _('Sometimes')),
        (1, _('Rarely')),
    ))
    """


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
    map_id = request.session.get('map_id')
    return render(request, 'network/graph.html', {
        'relation_groups': relation_groups,
        'group_first_relation': group_first_relation,
        'relation_types_grouped': dict(relation_types_grouped),
        'relation_types_flat': relation_types_flat,
        'add_node_form': EntityForm(prefix='node'),
        'add_stakeholder_form': StakeholderForm(prefix='stakeholder'),
        'map_form': MapForm(prefix='map'),
        'map_upload_form': MapUploadForm(),
        'map': map_id and Map.objects.get(id=map_id),
    })


@csrf_exempt
def graph_create(request):
    if request.is_ajax():
        form = MapForm(request.POST, prefix='map')
        if form.is_valid():
            m = form.save()
            request.session['map_id'] = m.id
            return JsonResponse({
                'id': m.id
            })


@csrf_exempt
def graph_update(request):
    if request.is_ajax():
        data = json.loads(request.body)
        map_id = request.session.get('map_id')
        m = Map.objects.get(id=map_id)
        m.graph = data.get('graph')
        m.save()
        return JsonResponse({
            'id': m.id
        })


def graph_view(request, map_id):
    relation_groups = dict(RELATION_GROUPS)
    relation_types_grouped = defaultdict(dict)
    relation_types_flat = {}
    for rt in RelationType.objects.all():
        relation_types_grouped[relation_groups[rt.group]][rt.id] = rt
        relation_types_flat[rt.id] = {
            'color': rt.color,
            'name': rt.name,
        }
    return render(request, 'network/graph_view.html', {
        'relation_types_flat': relation_types_flat,
        'map': Map.objects.get(id=map_id),
    })


@csrf_exempt
def graph_upload(request):
    if request.is_ajax():
        m = Map.objects.create(**request.POST)
        return JsonResponse({
            'id': m.id
        })
