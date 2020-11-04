import json
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from .models import Map, RelationType, Sector, Workshop, ORGANIZATION_SIZES


def index(request, workshop_slug=None):
    if workshop_slug:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        request.session['workshop'] = workshop.name
    else:
        workshop = None
    return render(request, 'mapper/index.html', {
        'workshop': workshop,
    })


class MapUploadForm(forms.Form):
    graph = forms.FileField(
        label=_('Map file'),
        help_text=_('Please select and upload the exported JSON map file.'),
    )


def sector_choices():
    return [
        (s.id, s.name) for s in Sector.objects.all()
    ]


class OrganisationForm(forms.Form):
    name = forms.CharField(
        label='Who are you making a stakeholder map of?',
        widget=forms.TextInput(attrs={'placeholder': 'Input name of organisation or team'}),
    )
    is_own = forms.BooleanField(
        label='Is this your own organisation or team?',
        required=False,
    )
    sector = forms.ChoiceField(
        label='What is your key sector?',
        help_text='Categories are obtained from the International Labour Organization.',
        choices=sector_choices,
    )
    size = forms.ChoiceField(
        label='What size is your organisation or team?',
        choices=(
            (1, '< 5'),
            (2, '5 - 9'),
            (3, '> 9'),
        )
    )
    purpose = forms.CharField(
        label='What is your main purpose for using this tool?',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe why you are here, what you hope to get out of it. '
                           'This helps us developing the tool better.'
        }),
    )

    def save(self, request, cleaned_data):
        data = request.session.get('data', {})
        data.update(cleaned_data)
        data.update({
            'graph': {
                'nodes': [{
                    'id': 0,
                    'label': cleaned_data['name'],
                    'x': 0, 'y': 0,
                    'size': 3,
                    'color': "#f00",
                }],
                'edges': [],
            }
        })
        request.session['data'] = data


class StakeholderNameForm(forms.Form):
    name = forms.CharField(label=_('Name of the stakeholder'))


def relation_type_choices():
    return [
        (rt.id, rt.name) for rt in RelationType.objects.all()
    ]


class EntityForm(forms.Form):
    name = forms.CharField(label=_('Name of the entity'))
    size = forms.ChoiceField(label=_('Size of the entity'), choices=ORGANIZATION_SIZES)
    relation_type = forms.ChoiceField(choices=relation_type_choices)
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


PAGES = {
    1: {
        'template': 'mapper/form.html',
        'context': {
            'form': OrganisationForm,
        },
    },
    2: {
        'template': 'mapper/map.html',
        'context': {
            'description': '''
                <p>Congratulations, you successfully created your stakeholder map!</p>
                <p>It’s looking rather empty here though, are you ready to add some key stakeholders?</p>
            ''',
        },
    },
}


def view_page(request, page_no, workshop_slug=None):
    page = PAGES.get(page_no)
    if not page:
        raise Http404
    if workshop_slug:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        request.session['workshop'] = workshop.name
    if request.method == 'POST':
        Form = page['context'].get('form')
        if Form:
            form = Form(request.POST)
            if form.is_valid():
                form.save(request, form.cleaned_data)
                return redirect('page_detail', page_no=page_no+1)
            else:
                page['context'].update({
                    'form': form,
                })
    page['context'].update({
        'data': request.session.get('data', {})
    })
    if workshop_slug:
        page['context'].update({
            'workshop': workshop,
        })
    return render(request, page['template'], page['context'])
