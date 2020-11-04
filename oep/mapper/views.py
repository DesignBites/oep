import json
from collections import defaultdict
import networkx as nx
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
            }
        })
        request.session['data'] = data


class StakeholderForm(forms.Form):
    customers = forms.CharField(
        label='Who are our key customers?',
        help_text='In other words, who receives our products, whose needs do we serve?',
        widget=forms.Textarea(),
    )
    supliers = forms.CharField(
        label='Who are our key suppliers?',
        help_text='In other words, who do we receive materials or resources from?',
        widget=forms.Textarea(),
    )
    collaborators = forms.CharField(
        label='Who are our key collaborators?',
        help_text='In other words, who do we develop our offerings, operations, or other solutions with?',
        widget=forms.Textarea(),
    )
    supporters = forms.CharField(
        label='Who are our key supporters?',
        help_text='In other words, who make our work possible or easier?',
        widget=forms.Textarea(),
    )

    def save(self, request, cleaned_data):
        data = request.session.get('data', {})
        data.update(cleaned_data)
        nodes = data['graph']['nodes']
        edges = data['graph'].get('edges', [])
        node_id = nodes[-1]['id'] + 1
        for stakeholder_type in cleaned_data.keys():
            for name in cleaned_data[stakeholder_type].split(','):
                name = name.strip()
                nodes.append({
                    'id': node_id,
                    'label': name,
                    'x': 0, 'y': 0,
                    'size': 3,
                    'color': "#f00",
                })
                edges.append({
                    'id': 'e' + str(node_id),
                    'source': 0,
                    'target': node_id,
                    'size': 1,
                    'label': stakeholder_type,
                    'color': '#fff',
                })
                node_id += 1
        data.update({
            'graph': {
                'nodes': nodes,
                'edges': edges,
            }
        })
        request.session['data'] = data
        request.session.modified = True


class StakeholderExtraForm(forms.Form):
    extra = forms.CharField(
        label='Anyone or any organization you’d like to add to your stakeholder map right away?',
        widget=forms.Textarea(),
    )

    def save(self, request, cleaned_data):
        data = request.session.get('data', {})
        data.update(cleaned_data)
        nodes = data['graph']['nodes']
        edges = data['graph'].get('edges', [])
        node_id = nodes[-1]['id'] + 1
        for stakeholder_type in cleaned_data.keys():
            for name in cleaned_data[stakeholder_type].split(','):
                name = name.strip()
                nodes.append({
                    'id': node_id,
                    'label': name,
                    'size': 3,
                    'color': "#f00",
                })
                edges.append({
                    'id': 'e' + str(node_id),
                    'source': 0,
                    'target': node_id,
                    'size': 1,
                    'label': stakeholder_type,
                    'color': '#fff',
                })
                node_id += 1
        positions = [
            (round(x, 2), round(y, 2)) for x, y in nx.circular_layout(list(range(len(nodes))), scale=1).values()
        ]
        i = 0
        print(nodes)
        print(positions)
        for node in nodes:
            node['x'], node['y'] = positions[i]
            i += 1
        data.update({
            'graph': {
                'nodes': nodes,
                'edges': edges,
            }
        })
        request.session['data'] = data
        request.session.modified = True


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
            'description': 'Let’s get you set up. To support you in identifying and selecting potential collaborators, '
                           'let’s start by getting to know your organisation or team.',
            'form': OrganisationForm,
        },
    },
    2: {
        'template': 'mapper/map.html',
        'context': {
            'description': '<p>Congratulations, you successfully created your stakeholder map!</p>'
                           '<p>It’s looking rather empty here though, are you ready to add some key stakeholders?</p>',
        },
    },
    3: {
        'template': 'mapper/form.html',
        'context': {
            'title': 'Add stakeholders',
            'description': "Let's start by adding some usual suspects. "
                           "Try to name at least three key stakeholders per question. "
                           "Separate stakeholders with commas, press tab to move to the next question.",
            'form': StakeholderForm,
        },
    },
    4: {
        'template': 'mapper/form.html',
        'context': {
            'title': 'Add stakeholders',
            'description': "For food and beverage SMEs, we’ve found 6 groups of development influencers and collaborators."
                           "<ul>"
                               "<li>customers and consumer communities,</li>"
                               "<li>other SMEs in the region or product niche,</li>"
                               "<li>the wider food and beverage ecosystem (e.g. chefs, cafes),</li>"
                               "<li>the supply and distribution chain (e.g. farmers, importers, retail chains),</li>"
                               "<li>other organizations (eg public funders, universities, associations, companies "
                                   "in other industries such as eg cosmetics or clothing), and</li>"
                               "<li>personal networks (friends, family, hobbies)</li>"
                           "</ul>",
            'form': StakeholderExtraForm,
        },
    },
    5: {
        'template': 'mapper/map.html',
        'context': {
            'description': "Awesome, look at all your stakeholders floating around you! "
                           "I’m sure you relate to them in different ways though, "
                           "are you ready to describe the relations to these stakeholders?",
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
    next_page = None
    if not page['context'].get('form'):
        next_page = page_no + 1
        if not next_page in PAGES:
            next_page = None
    page['context'].update({
        'data': request.session.get('data', {}),
        'next_page': next_page,
    })
    if workshop_slug:
        page['context'].update({
            'workshop': workshop,
        })
    return render(request, page['template'], page['context'])
