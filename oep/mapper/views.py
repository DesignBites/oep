import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django import forms
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from .models import Map, Sector, Purpose, Workshop, StakeholderType, PageInfo
from .layouts import circular_layout, ring_layout, venn_layout, suggest_layout


def reset_session(request, map_data={}):
    mapper_variables = [
        'stakeholders',
        'organization',
        'custom_similarity_parameter',
        'workshop',
        'last_page_no',
    ]
    for key in mapper_variables:
        value = map_data.get(key)
        if value:
            request.session[key] = value
        else:
            try:
                del request.session[key]
            except KeyError:
                pass


def index(request, workshop_slug=None):
    workshop = None
    if workshop_slug:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        request.session['workshop'] = workshop.name
    return render(request, 'mapper/index.html', {
        'workshop': workshop,
    })


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
        request.session['organization'] = cleaned_data


def organisation_form(request, **kwargs):
    if request.method == 'POST':
        form = OrganisationForm(request.POST)
        if form.is_valid():
            form.save(request, form.cleaned_data)
            if kwargs.get('page_no'):
                return redirect('mapper_page', page_no=kwargs['page_no']+1)
    reset_session(request)
    form = OrganisationForm()
    kwargs.update({
        'form': form,
    })
    return render(request, 'mapper/organisation_form.html', kwargs)


class MapUploadForm(forms.Form):
    map = forms.FileField(
        label=_('Map file'),
        help_text=_('Please select and upload the exported JSON file.'),
    )


def upload_map(request):
    if request.method == 'POST':
        form = MapUploadForm(request.POST, request.FILES)
        if form.is_valid():
            map_data = json.loads(form.cleaned_data['map'].read())
            print(map_data)
            reset_session(request, map_data)
            page_no = map_data.get('last_page_no', 1)
            return redirect('mapper_page', page_no=page_no)
        else:
            messages.warning(request, form.errors)
            messages.warning(request, 'The file is not valid. Please start over.')
            return redirect('mapper_page', page_no=1)
    return render(request, 'mapper/upload.html', {
        'form': MapUploadForm(),
    })


@csrf_exempt
def connections_save(request):
    if request.is_ajax():
        data = json.loads(request.body)
        stakeholders = request.session.get('stakeholders', {})
        for similarity_type, stakeholder_names in data.items():
            for name in stakeholder_names:
                name = str(name)  # for the rare case of all numeric names
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


class StakeholderBatchForm(forms.Form):
    def __init__(self, batch_no, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stakeholder_types = StakeholderType.objects.filter(batch_no=batch_no)
        i = 1
        for stakeholder_type in stakeholder_types:
            attrs = {
                'data-role': 'tagsinput',
                'tabindex': i,
            }
            if i == 1:
                attrs.update({
                    'autofocus': 'autofocus'
                })
            self.fields[stakeholder_type.name] = forms.CharField(
                label=stakeholder_type.question,
                help_text=stakeholder_type.description,
                required=False,
                widget=forms.TextInput(attrs=attrs),
            )
            i += 1

    def save(self, request, cleaned_data):
        stakeholders = request.session.get('stakeholders') or {}
        print(stakeholders)
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
        form = StakeholderBatchForm(batch_no, request.POST)
        if form.is_valid():
            form.save(request, form.cleaned_data)
            if kwargs.get('page_no'):
                return redirect('mapper_page', page_no=kwargs['page_no']+1)
    else:
        form = StakeholderBatchForm(batch_no)
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
        # called via the menu
        kwargs.update({
            'show_menu': True,
        })
        page_info = PageInfo.objects.filter(page='circles').first()
        if page_info:
            kwargs.update({
                'title': page_info.title,
                'description': page_info.description,
            })
    kwargs.update({
        'graph': ring_layout(stakeholders),
    })
    if 'stakeholder_form' not in kwargs:
        kwargs.update({
            'stakeholder_form': StakeholderForm(
                show_similarities=True,
                custom_similarity_parameter=request.session.get('custom_similarity_parameter'),
            ),
        })
    return render(request, 'mapper/ring.html', kwargs)


def venn_view(request, **kwargs):
    stakeholders = request.session.get('stakeholders', {})
    if kwargs == {}:
        # called via the menu
        kwargs.update({
            'show_menu': True,
        })
        page_info = PageInfo.objects.filter(page='venn').first()
        if page_info:
            kwargs.update({
                'title': page_info.title,
                'description': page_info.description,
            })
    kwargs.update(venn_layout(stakeholders))
    if 'stakeholder_form' not in kwargs:
        kwargs.update({
            'stakeholder_form': StakeholderForm(
                show_similarities=True,
                custom_similarity_parameter=request.session.get('custom_similarity_parameter'),
            ),
        })
    return render(request, 'mapper/venn.html', kwargs)


def suggest_view(request, **kwargs):
    stakeholders = request.session.get('stakeholders', {})
    if kwargs == {}:
        # called via the menu
        kwargs.update({
            'show_menu': True,
        })
        page_info = PageInfo.objects.filter(page='suggestions').first()
        if page_info:
            kwargs.update({
                'title': page_info.title,
                'description': page_info.description,
            })
    kwargs.update(suggest_layout(stakeholders))
    return render(request, 'mapper/suggest.html', kwargs)


class StakeholderForm(forms.Form):
    name = forms.CharField(
        label='What is the name of this organisation?',
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
    values = forms.BooleanField(
        label='We have similar values',
        required=False,
    )
    working = forms.BooleanField(
        label='We have similar ways of working',
        required=False,
    )
    resources = forms.BooleanField(
        label='We have similar resources and skills',
        required=False,
    )
    custom = forms.BooleanField(
        required=False,
    )

    def __init__(self, *args, **kwargs):
        try:
            custom_similarity_parameter = kwargs.pop('custom_similarity_parameter')
        except KeyError:
            custom_similarity_parameter = None
        try:
            show_similarities = kwargs.pop('show_similarities')
        except KeyError:
            show_similarities = False
        super().__init__(*args, **kwargs)
        if not custom_similarity_parameter and not self.is_bound:
            del self.fields['custom']
        else:
            self.fields['custom'].label = "%s is true" % custom_similarity_parameter
        if not show_similarities and not self.is_bound:
            del self.fields['values']
            del self.fields['working']
            del self.fields['resources']


def node_add(request, **kwargs):
    if request.method == 'POST':
        form = StakeholderForm(request.POST)
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
            custom = data.get('custom') and 1 or 0
            stakeholders[data['name']] = {
                'interact': int(data['interact']),
                'collaborate': int(data['collaborate']),
                'similarities': similarities,
                'custom': custom,
            }
            request.session['stakeholders'] = stakeholders
            if kwargs.get('next_page'):
                return redirect('mapper_page', page_no=kwargs['next_page'])
            else:
                return redirect('mapper_ring')
    else:
        form = StakeholderForm(
            custom_similarity_parameter=request.session.get('custom_similarity_parameter')
        )
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
        form = StakeholderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            stakeholders = request.session.get('stakeholders', {})
            similarities = []
            if data.get('values'):
                similarities.append('values')
            if data.get('working'):
                similarities.append('working')
            if data.get('resources'):
                similarities.append('resources')
            custom = data.get('custom') and 1 or 0
            stakeholders[data['name']] = {
                'interact': int(data['interact']),
                'collaborate': int(data['collaborate']),
                'similarities': similarities,
                'custom': custom,
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
    },
    {
        'view': map_view,
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 1,
        }
    },
    {
        'view': map_view,
        'context': {
            'layout': circular_layout,
        },
    },
    {
        'view': grid_view,
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'stakeholder_form': StakeholderForm(),
        },
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 2,
        },
    },
    {
        'view': grid_view,
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'stakeholder_form': StakeholderForm(),
        },
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 3,
        },
    },
    {
        'view': grid_view,
        'context': {
        },
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'stakeholder_form': StakeholderForm(),
        },
    },
    {
        'view': add_stakeholders,
        'context': {
            'batch_no': 4,
        },
    },
    {
        'view': grid_view,
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
           'stakeholder_form': StakeholderForm(),
        },
    },
    {
        'view': picker_view,
        'context': {
            'layout': circular_layout,
            'similarity_type': 'values',
            'similarity_icon': 'a',
        },
    },
    {
        'view': picker_view,
        'context': {
            'layout': circular_layout,
            'similarity_type': 'working',
            'similarity_icon': 'c',
        },
    },
    {
        'view': picker_view,
        'context': {
            'layout': circular_layout,
            'similarity_type': 'resources',
            'similarity_icon': 'd',
        },
    },
    # menu is enabled here!; add / edit of similarity parameters enabled here!
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'show_menu': True,
        },
    },
    {
        'view': add_custom_similarity,
    },
    {
        'view': picker_view,
        'context': {
            'layout': circular_layout,
            'similarity_type': 'custom',
            'similarity_icon': 'b',
        },
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
            'show_menu': True,
        },
    },
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
    request.session['last_page_no'] = page_no
    if workshop_slug:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        request.session['workshop'] = workshop.name
    next_page = None
    context = page.get('context', {})
    if not context.get('form'):
        next_page = page_no + 1
        if next_page > len(PAGES):
            next_page = None
    page_info = PageInfo.objects.filter(page=str(page_no)).first()
    if page_info:
        context.update({
            'title': page_info.title,
            'description': page_info.description,
        })
    context.update({
        'stakeholders': request.session.get('stakeholders', {}),
        'page_no': page_no,
        'next_page': next_page,
    })
    if workshop_slug:
        context.update({
            'workshop': workshop,
        })
    return page['view'](request, **context)


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
