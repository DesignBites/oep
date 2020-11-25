import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from .models import Map, Sector, Purpose, Workshop, StakeholderType
from .layouts import circular_layout, ring_layout, venn_layout, suggest_layout


def index(request, workshop_slug=None):
    request.session['stakeholders'] = {}
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
        help_text=_('Please select and upload the exported JSON file.'),
    )


@csrf_exempt
def connections_save(request):
    if request.is_ajax():
        data = json.loads(request.body)
        stakeholders = request.session['stakeholders']
        for similarity_type, stakeholder_names in data.items():
            for name in stakeholder_names:
                similarities = stakeholders[name].get('similarities', [])
                similarities.append(similarity_type)
                stakeholders[name]['similarities'] = list(set(similarities))
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


class StakeholderForm(forms.Form):
    def __init__(self, batch_no, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stakeholder_types = StakeholderType.objects.filter(batch_no=batch_no)
        for stakeholder_type in stakeholder_types:
            self.fields[stakeholder_type.name] = forms.CharField(
                label=stakeholder_type.question,
                help_text=stakeholder_type.description,
                required=False,
                widget=forms.TextInput(attrs={
                    'data-role': 'tagsinput',
                }),
            )

    def save(self, request, cleaned_data):
        stakeholders = request.session.get('stakeholders', {})
        for stakeholder_type in cleaned_data.keys():
            for name in cleaned_data[stakeholder_type].split(','):
                name = name.strip()
                if name:
                    if name in stakeholders:
                        stakeholders[name]['types'].append(stakeholder_type)
                    else:
                        stakeholders[name] = {}
                        stakeholders[name]['types'] = [stakeholder_type]
        request.session['stakeholders'] = stakeholders


def add_stakeholders(request, **kwargs):
    batch_no = kwargs['batch_no']
    if request.method == 'POST':
        form = StakeholderForm(batch_no, request.POST)
        if form.is_valid():
            form.save(request, form.cleaned_data)
            if kwargs.get('page_no'):
                return redirect('mapper_page', page_no=kwargs['page_no']+1)
    else:
        form = StakeholderForm(batch_no)
    kwargs.update({
        'form': form,
    })
    return render(request, 'mapper/add_stakeholders.html', kwargs)


class SimilarityTypeForm(forms.Form):
    similarity = forms.CharField(
        label='What is a key parameter for you?',
        help_text='In other words, which other professional, or personal, characteristic '
                  'is important to you to describe your relationships with?',
        required=False,
    )

    def save(self, request, cleaned_data):
        request.session['custom_similarity_parameter'] = cleaned_data['similarity']


def add_custom_similarity(request, **kwargs):
    if request.method == 'POST':
        form = SimilarityTypeForm(request.POST)
        if form.is_valid():
            form.save(request, form.cleaned_data)
            if kwargs.get('page_no'):
                return redirect('mapper_page', page_no=kwargs['page_no']+1)
    else:
        form = SimilarityTypeForm()
    kwargs.update({
        'form': form,
    })
    return render(request, 'mapper/add_custom_similarity.html', kwargs)


def ring_view(request, **kwargs):
    stakeholders = request.session.get('stakeholders', {})
    if kwargs == {}:
        kwargs.update({
            'show_menu': True,
        })
    kwargs.update({
        'graph': ring_layout(stakeholders),
        'stakeholder_form': StakeholderAddForm(),
    })
    return render(request, 'mapper/ring.html', kwargs)


def venn_view(request, **kwargs):
    stakeholders = request.session.get('stakeholders', {})
    if kwargs == {}:
        kwargs.update({
            'show_menu': True,
        })
    kwargs.update({
        'graph': venn_layout(stakeholders),
        'stakeholder_form': StakeholderAddForm(),
    })
    return render(request, 'mapper/venn.html', kwargs)


def suggest_view(request, **kwargs):
    stakeholders = request.session.get('stakeholders', {})
    if kwargs == {}:
        kwargs.update({
            'show_menu': True,
        })
    kwargs.update(suggest_layout(stakeholders))
    return render(request, 'mapper/suggest.html', kwargs)


class StakeholderAddForm(forms.Form):
    name = forms.CharField(
        label='What is the name of this organisation?',
    )
    values = forms.BooleanField(
        label='Do you have similar values?',
        required=False,
    )
    working = forms.BooleanField(
        label='Do you have similar ways of working?',
        required=False,
    )
    resources = forms.BooleanField(
        label='Do you have similar resources and skills?',
        required=False,
    )
    custom = forms.CharField(
        label='Are you similar in any other way?',
        help_text='Please specify',
        required=False,
    )
    interact = forms.ChoiceField(
        label='How often do you interact with each other?',
        choices=(
            (3, 'Regularly'),
            (2, 'Sometimes'),
            (1, 'Hardly ever'),
        )
    )
    collaborate = forms.ChoiceField(
        label='How often have you collaborated creatively with each other?',
        choices=(
            (3, 'Many times'),
            (2, 'Once or twice'),
            (1, 'Never'),
        )
    )


def node_add(request, **kwargs):
    if request.method == 'POST':
        form = StakeholderAddForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            stakeholders = request.session.get('stakeholders', {})
            similarities = []
            if data.get('values'):
                similarities.append('values')
            if data.get('working'):
                similarities.append('working')
            if data.get('resources'):
                similarities.append('resources')
            if data.get('custom'):
                similarities.append(data['custom'])
            stakeholders[data['name']] = {
                'similarities': similarities,
                'interact': int(data['interact']),
                'collaborate': int(data['collaborate']),
            }
            request.session['stakeholders'] = stakeholders
            if kwargs.get('next_page'):
                return redirect('mapper_page', page_no=kwargs['next_page'])
            else:
                return redirect('mapper_ring')
    else:
        form = StakeholderAddForm()
    if kwargs == {}:
        kwargs.update({
            'show_menu': True,
        })
    kwargs.update({
        'form': form,
    })
    return render(request, 'mapper/add.html', kwargs)


@csrf_exempt
def node_update(request):
    if request.method == 'POST':
        form = StakeholderAddForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            stakeholders = request.session.get('stakeholders', {})
            similarities = []
            if data.get('values'):
                similarities.append('values')
            if data.get('working'):
                similarities.append('working')
            if data.get('resources'):
                similarities.append('resources')
            if data.get('custom'):
                similarities.append(data['custom'])
            stakeholders[data['name']] = {
                'similarities': similarities,
                'interact': int(data['interact']),
                'collaborate': int(data['collaborate']),
            }
            request.session['stakeholders'] = stakeholders
            return JsonResponse({
                'stakeholders': stakeholders,
            })


@csrf_exempt
def node_delete(request):
    if request.method == 'POST':
        print(request.POST)
        name = request.POST.get('name')
        print(name)
        stakeholders = request.session.get('stakeholders', {})
        try:
            del stakeholders[name]
        except KeyError:
            pass
        request.session['stakeholders'] = stakeholders
        return JsonResponse({
            'stakeholders': stakeholders,
        })



def map_extend(request):
    stakeholders = request.session.get('stakeholders', {})
    return render(request, 'mapper/suggest.html', {
        'graph': suggest_layout(stakeholders),
    })


@csrf_exempt
def approve_terms(request):
    request.session['terms_ok'] = True
    return JsonResponse({
        'terms_ok': True,
    })


@csrf_exempt
def map_save(request):
    map_session = request.session.get('map')
    if map_session:
        stakeholders = request.session['stakeholders']
        if map_session.get('id'):
            m = Map.objects.get(id=map_session['id'])
            m.stakeholders = stakeholders
            m.save()
        else:
            m = Map.objects.create(**{
                'name': map_session['name'],
                'workshop': request.session['workshop'],
                'is_own': map_session['is_own'],
                'sector': get_object_or_404(Sector, id=map_session['sector']),
                'size': map_session['size'],
                'purpose': map_session['purpose'] and get_object_or_404(Purpose, id=map_session['purpose']) or None,
                'stakeholders': stakeholders,
            })
            map_session['id'] = m.id
            request.session.modified = True
    return JsonResponse({})


def sector_choices():
    return [
        (s.id, s.name) for s in Sector.objects.all()
    ]


class OrganisationForm(forms.Form):
    name = forms.CharField(
        label='Which organization are you making a stakeholder map of?',
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


def organisation_form(request, **kwargs):
    if request.method == 'POST':
        form = OrganisationForm(request.POST)
        if form.is_valid():
            form.save(request, form.cleaned_data)
            if kwargs.get('page_no'):
                return redirect('mapper_page', page_no=kwargs['page_no']+1)
    else:
        form = OrganisationForm()
    kwargs.update({
        'form': form,
    })
    return render(request, 'mapper/organisation_form.html', kwargs)


def map_view(request, **kwargs):
    layout = kwargs.get('layout')
    if layout:
        kwargs.update({
            'graph': layout(kwargs['stakeholders'])
        })
    return render(request, 'mapper/map.html', kwargs)


def grid_view(request, **kwargs):
    return render(request, 'mapper/grid.html', kwargs)


def picker_view(request, **kwargs):
    layout = kwargs.get('layout')
    if layout:
        kwargs.update({
            'graph': layout(kwargs['stakeholders'])
        })
    return render(request, 'mapper/picker.html', kwargs)


# the page flow

PAGES = [
    {
        'view': organisation_form,
        'context': {
            'description': 'Let’s get you set up. To support you in identifying and selecting potential collaborators, '
                           'let’s start by getting to know your organisation or team.',
        },
    },
    {
        'view': map_view,
        'context': {
            'description': '<p>Congratulations, you successfully created your stakeholder map!</p>'
                           '<p>It’s looking rather empty here though, are you ready to add some key stakeholders?</p>',
        },
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 1,
            'description': "Let's start by adding some usual suspects. "
                           "Try to name at least three key stakeholders per question. "
                           "Separate stakeholders with commas, press tab to move to the next question.",
        }
    },
    {
        'view': map_view,
        'context': {
            'layout': circular_layout,
            'description': "<p>Awesome, look at all your stakeholders floating around you!</p>"
                           "<p>I’m sure you relate to them in different ways though, "
                           "are you ready to describe the relations to these stakeholders?</p>",
        },
    },
    {
        'view': grid_view,
        'context': {
            'title': 'Frequency and depth of contact',
            'description': "Now indicate for each stakeholder in the axis diagram how often you interact, "
                           "and how actively you collaborate creatively together.",
        },
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'description': "<p>Awesome, look at all your stakeholders floating around you!</p>"
                           "<p>I’m sure you relate to them in different ways though, "
                           "are you ready to describe the relations to these stakeholders?</p>",
        },
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 2,
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
        },
    },
    {
        'view': grid_view,
        'context': {
            'title': 'Frequency and depth of contact',
            'description': "Now indicate for each stakeholder in the axis diagram how often you interact, "
                           "and how actively you collaborate creatively together.",
        },
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'description': "<p>Well done!</p>"
                           "<p>If you made a mistake, you can edit stakeholders by clicking on them.</p>"
                           "<p>There are more stakeholders to add though, are you ready to expand your network?</p>",
        },
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 3,
            'description': "Let's take it a step further down the chain. "
                           "Again, try to name at least three key stakeholders per question. "
                           "Separate stakeholders with commas, press tab to move to the next question.",
        },
    },
    {
        'view': grid_view,
        'context': {
            'title': 'Frequency and depth of contact',
            'description': "Now indicate for each stakeholder in the axis diagram how often you interact, "
                           "and how actively you collaborate creatively together.",
        },
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'description': "<p>Well done!</p>"
                           "<p>If you made a mistake, you can edit stakeholders by clicking on them.</p>"
                           "<p>There are more stakeholders to add though, are you ready to expand your network?</p>",
        },
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 4,
            'description': "Let's take an even wider look at the ecosystem. "
                           "Again, try to name at least three key stakeholders per question. "
                           "Separate stakeholders with commas, press tab to move to the next question.",
        },
    },
    {
        'view': grid_view,
        'context': {
            'title': 'Frequency and depth of contact',
            'description': "Now indicate for each stakeholder in the axis diagram how often you interact, "
                           "and how actively you collaborate creatively together.",
        },
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'description': "<p>Awesome, you should now have most of your stakeholders here.</p>"
                           "<p>When identifying new people to collaborate with, it’s important to consider "
                           "how potential collaborators are either similar or complementary to you.</p>"
                           "<p>Are you ready to indicate their similarity?</p>"
        },
    },
    {
        'view': picker_view,
        'context': {
            'title': 'Similarity of values',
            'description': "Let's start by indicating who of these key stakeholders are more similar to you. "
                           "For each stakeholder, indicate whether you feel their values, "
                           "ways of working, and resources and skills are similar to you.<br>"
                           "First, select the stakeholders that have similar <strong>values</strong>.",
            'layout': circular_layout,
            'similarity_type': 'values',
            'similarity_icon': 'a',
        },
    },
    {
        'view': picker_view,
        'context': {
            'title': 'Similarity of ways of working',
            'description': "Now, select the stakeholders that have similar <strong>ways of working</strong>.",
            'layout': circular_layout,
            'similarity_type': 'working',
            'similarity_icon': 'c',
        },
    },
    {
        'view': picker_view,
        'context': {
            'title': 'Similarity of resources and skills',
            'description': "Lastly, select the stakeholders that have similar <strong>resources and skills</strong>.",
            'layout': circular_layout,
            'similarity_type': 'resources',
            'similarity_icon': 'd',
        },
    },
    # menu is enabled here!
    {
        'view': ring_view,
        'context': {
            'description': "<p>Awesome, you now have a stakeholder map.</p>"
                           "<p>You can already play with the filters and different visualisations to reveal "
                           "potential collaborators based on your similarity.</p>"
                           "<p>You can also edit or delete stakeholders by clicking on them.</p>"
                           "<p>There are more stakeholders to add though, are you ready to expand your network?</p>",
            'layout': ring_layout,
            'show_menu': True,
        },
    },
    {
        'view': add_custom_similarity,
        'context': {
            'title': 'Similarity of a parameter of your choice',
            'description': "<p>You can also create your own parameter to compare stakeholders with.</p>",
            'show_menu': True,
        },
    },
    {
        'view': picker_view,
        'context': {
            'title': 'Similarity of a parameter of your choice',
            'description': "Now, select the stakeholders for which your parameter is true: ",
            'layout': circular_layout,
            'similarity_type': 'custom',
            'similarity_icon': 'b',
            'show_menu': True,
        },
    },
    {
        'view': ring_view,
        'context': {
            'description': "<p>Awesome, you now have a stakeholder map.</p>"
                           "<p>You can already play with the filters and different visualisations to reveal "
                           "potential collaborators based on your similarity.</p>"
                           "<p>You can also edit or delete stakeholders by clicking on them.</p>"
                           "<p>There are more stakeholders to add though, are you ready to expand your network?</p>",
            'layout': ring_layout,
            'show_menu': True,
        },
    },
    """
    {
        'view': node_add,
        'context': {
        },
    },
    {
        'view': ring_view,
        'context': {
            'description': "<p>Awesome, you now have a stakeholder map.</p>"
                           "<p>You can already play with the filters and different visualisations to reveal "
                           "potential collaborators based on your similarity.</p>"
                           "<p>You can also edit or delete stakeholders by clicking on them.</p>"
                           "<p>There are more stakeholders to add though, are you ready to expand your network?</p>",
            'layout': ring_layout,
        },
    },
    {
        'view': venn_view,
        'context': {
            'layout': venn_layout,
        },
    },
    {
        'view': suggest_view,
        'context': {
            'layout': suggest_layout,
            'modal': 'modalTerms',
        },
    },
    """
]


FILTERS_DICT = {
    'interact': {
        'title': 'Frequency of interactions',
        'options': (
            (3, 'often'),
            (2, 'regularly'),
            (1, 'hardly ever'),
        ),
    },
    'collaborate': {
        'title': 'Depth of collaborations',
        'options': (
            (3, 'many'),
            (2, 'once or twice'),
            (1, 'never'),
        ),
    },
    'similarity': {
        'title': 'Depth of collaborations',
        'options': (
            ('values', ''),
            (2, 'once or twice'),
            (1, 'never'),
        )
    },
}


def page_view(request, page_no, workshop_slug=None):
    try:
        page = PAGES[page_no-1]
    except IndexError:
        raise Http404
    if workshop_slug:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        request.session['workshop'] = workshop.name
    next_page = None
    if not page['context'].get('form'):
        next_page = page_no + 1
        if next_page > len(PAGES):
            next_page = None
    page['context'].update({
        'map': request.session.get('map', {}),  # entity profile data
        'stakeholders': request.session.get('stakeholders', {}),
        'page_no': page_no,
        'next_page': next_page,
    })
    if workshop_slug:
        page['context'].update({
            'workshop': workshop,
        })
    return page['view'](request, **page['context'])


"""
stakeholders = {
    StakeholderName: {
        types: [customer | supplier | collaborator | supporter | extra]
        similarities: [values | working | resources | custom]
        interact: 1 - 3
        collaborate: 1 - 3
    }
}
"""
