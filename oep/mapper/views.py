import json
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from .layouts import circular_layout, ring_layout
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
        request.session['map'] = cleaned_data
        request.session.modified = True


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
        stakeholders = {}
        for stakeholder_type in cleaned_data.keys():
            for name in cleaned_data[stakeholder_type].split(','):
                name = name.strip()
                if name in stakeholders:
                    stakeholders[name]['types'].append(stakeholder_type)
                else:
                    stakeholders[name] = {}
                    stakeholders[name]['types'] = [stakeholder_type]
        request.session['stakeholders'] = stakeholders


class StakeholderExtraForm(forms.Form):
    extra = forms.CharField(
        label='Anyone or any organization you’d like to add to your stakeholder map right away?',
        widget=forms.Textarea(),
    )

    def save(self, request, cleaned_data):
        stakeholders = request.session.get('stakeholders', {})
        stakeholder_type = 'extra'
        for name in cleaned_data[stakeholder_type].split(','):
            name = name.strip()
            if name in stakeholders:
                stakeholders[name]['types'].append(stakeholder_type)
            else:
                stakeholders[name] = {}
                stakeholders[name]['types'] = [stakeholder_type]
        request.session['stakeholders'] = stakeholders


class SimilarityTypeForm(forms.Form):
    similarity = forms.CharField(
        label='What is a key parameter for you?',
        help_text='In other words, which other professional, or personal, characteristic '
                  'is important to you to describe your relationships with?',
        required=False,
    )


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
def graph_save(request):
    if request.is_ajax():
        data = json.loads(request.body)
        data.update({
            'graph': data.get('graph'),
        })
        request.session['data'] = data
        request.session.modified = True
        #m = Map.objects.get(id=map_id)
        #m.graph = data.get('graph')
        #m.save()
        return JsonResponse({
            'data': data,
        })


@csrf_exempt
def connections_save(request):
    if request.is_ajax():
        data = json.loads(request.body)
        print(data)
        stakeholders = request.session['stakeholders']
        for similarity_type, stakeholder_names in data.items():
            for name in stakeholder_names:
                if 'similarities' in stakeholders[name]:
                    stakeholders[name]['similarities'].append(similarity_type)
                else:
                    stakeholders[name]['similarities'] = [similarity_type]
        request.session['stakeholders'] = stakeholders
        request.session.modified = True
        return JsonResponse({
            'data': data,
        })


@csrf_exempt
def grid_save(request):
    if request.is_ajax():
        stakeholders = request.session['stakeholders']
        data = json.loads(request.body)
        print(data)
        for stakeholder_name, connection in data.items():
            stakeholders[stakeholder_name]['interact'] = connection['interact']
            stakeholders[stakeholder_name]['collaborate'] = connection['collaborate']
        request.session['stakeholders'] = stakeholders
        request.session.modified = True
        return JsonResponse({
            'data': data,
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
            'description': "<p>Awesome, look at all your stakeholders floating around you!</p>"
                           "<p>I’m sure you relate to them in different ways though, "
                           "are you ready to describe the relations to these stakeholders?</p>",
            'graph_layout': circular_layout,
        },
    },
    6: {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of values',
            'description': "Let's start by indicating who of these key stakeholders are more similar to you. "
                           "For each stakeholder, indicate whether you feel their values, "
                           "ways of working, and resources and skills are similar to you.<br>"
                           "First, select the stakeholders that have similar <strong>values</strong>.",
            'similarity_type': 'values',
            'graph_layout': circular_layout,
        },
    },
    7: {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of ways of working',
            'description': "Now, select the stakeholders that have similar <strong>ways of working</strong>.",
            'similarity_type': 'working',
            'graph_layout': circular_layout,
        },
    },
    8: {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of resources and skills',
            'description': "Lastly, select the stakeholders that have similar <strong>resources and skills</strong>.",
            'similarity_type': 'resources',
            'graph_layout': circular_layout,
        },
    },
    9: {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of a parameter of your choice',
            'description': "<p>You can also create your own parameter to compare stakeholders with.</p>",
            'similarity_type': 'user_defined',
            'similarity_type_form': SimilarityTypeForm(),
            'graph_layout': circular_layout,
        },
    },
    10: {
        'template': 'mapper/grid.html',
        'context': {
            'title': 'Frequency and depth of contact',
            'description': "Now select the stakeholders and tap on the right grid to indicate how much you interact, "
                           "and collaborate creatively together.",
        },
    },
    11: {
        'template': 'mapper/ring.html',
        'context': {
            'title': 'Frequency and depth of contact',
            'description': "<p>Awesome, you now have a stakeholder map.</p>"
                           "<p>You can already play with the filters and different visualisations to reveal "
                           "potential collaborators based on your similarity.</p>"
                           "<p>You can also edit or delete stakeholders by clicking on them.</p>"
                           "<p>There are more stakeholders to add though, are you ready to expand your network?</p>",
            'graph_layout': ring_layout,
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
        'map': request.session.get('map', {}),  # entity profile data
        'stakeholders': request.session.get('stakeholders', {}),
        'next_page': next_page,
    })
    if workshop_slug:
        page['context'].update({
            'workshop': workshop,
        })
    if page['context'].get('graph_layout'):
        page['context']['graph'] = page['context'].get('graph_layout')(
            request.session['stakeholders']
        )
    return render(request, page['template'], page['context'])
