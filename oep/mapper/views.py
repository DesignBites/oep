import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django import forms
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from crispy_forms.helper import FormHelper
from .models import Map, Sector, Workshop, StakeholderType, PageInfo
from .layouts import circular_layout, ring_layout, venn_layout, suggest_layout, get_node_icon_prefix, NODE_ICON_NAME


SESSION_VARIABLES = [
    'stakeholders',
    'organization',
    'custom_similarity_parameter',
    'workshop',
    'last_page_no',
]


def approve_terms(request):
    terms = request.GET.get('terms')
    if terms:
        if terms == 'yes':
            request.session['terms_ok'] = True
        else:
            terms = 'no'
            request.session['terms_ok'] = False
        # reset session variables
        for key in SESSION_VARIABLES:
            try:
                del request.session[key]
            except KeyError:
                pass
        if request.is_ajax():
            return JsonResponse({
                'terms': terms,
            })
        else:
            return redirect('mapper_page', page_no=1)
    context = {}
    page_info = PageInfo.objects.filter(page='terms').first()
    if page_info:
        context.update({
            'title': page_info.title,
            'description': page_info.description,
        })
    return render(request, 'mapper/terms.html', context)


def index(request, workshop_slug=None):
    workshop = None
    if workshop_slug:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        request.session['workshop'] = workshop.name
    context = {
        'workshop': workshop,
    }
    return render(request, 'mapper/index.html', context)


def sector_choices():
    return [
        (s.id, s.name) for s in Sector.objects.all()
    ]


class OrganisationForm(forms.Form):
    name = forms.CharField(
        label='Which organization are you making a stakeholder map of?',
        widget=forms.TextInput(attrs={'placeholder': 'Input name of organisation or team'}),
    )
    is_own = forms.ChoiceField(
        label='Is this your own organisation or team?',
        choices=(
            (True, 'Yes'),
            (False, 'No'),
        ),
        widget=forms.RadioSelect(),
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
        ),
        widget=forms.RadioSelect(),
    )
    purpose = forms.CharField(
        label='What is your main purpose for using this tool?',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe why you are here, what you hope to get out of it. '
                           'This helps us developing the tool better.',
            'rows': 2,
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-6'
        self.helper.field_class = 'col-md-6'

    def save(self, request, cleaned_data):
        request.session['organization'] = cleaned_data


def organisation_form(request, **kwargs):
    if request.method == 'POST':
        form = OrganisationForm(request.POST)
        if form.is_valid():
            form.save(request, form.cleaned_data)
            if kwargs.get('page_no'):
                return redirect('mapper_page', page_no=kwargs['page_no']+1)
    else:
        if request.session.get('organization'):
            form = OrganisationForm(
                request.session.get('organization')
            )
        else:
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
            try:
                map_data = json.loads(form.cleaned_data['map'].read())
            except json.decoder.JSONDecodeError:
                messages.warning(
                    request,
                    mark_safe(
                        'The file is not valid. Please start over here or <a href="%s">upload another file</a>.' % (
                            reverse('mapper_upload'),
                        ),
                    ),
                )
                return redirect('mapper_page', page_no=1)
            for key in SESSION_VARIABLES:
                value = map_data.get(key)
                if value:
                    request.session[key] = value
                else:
                    try:
                        del request.session[key]
                    except KeyError:
                        pass
            page_no = map_data.get('last_page_no', 1)
            return redirect('mapper_page', page_no=page_no)
        else:
            messages.warning(
                request,
                mark_safe(
                    'The file is not valid. Please start over here or <a href="%s">upload another file</a>.' % (
                        reverse('mapper_upload'),
                    ),
                ),
            )
            return redirect('mapper_page', page_no=1)
    return render(request, 'mapper/upload.html', {
        'form': MapUploadForm(),
    })


@csrf_exempt
def connections_save(request):
    # update similarities for the given type(s)
    # e.g.: {'values': ['AAA', 'BBB']}
    if request.is_ajax():
        data = json.loads(request.body)
        stakeholders = request.session.get('stakeholders', {})
        for name, current_data in stakeholders.items():
            similarities = stakeholders[name].get('similarities', [])
            for similarity_type, stakeholder_names in data.items():
                # stakeholder_names: updated names for this type of similarity
                stakeholder_names = map(str, stakeholder_names)  # for the rare case of all numeric names
                if name in stakeholder_names:
                    if similarity_type not in similarities:
                        # newly added
                        similarities.append(similarity_type)
                else:
                    if similarity_type in similarities:
                        # newly removed
                        similarities.remove(similarity_type)
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
        # FIXME: crispy helpers not working
        #self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        #self.helper.label_class = 'col-md-6'
        #self.helper.field_class = 'col-md-6'

    def save(self, request, cleaned_data):
        stakeholders = request.session.get('stakeholders') or {}
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
        stakeholders = kwargs.get('stakeholders', {})
        for field in form:
            initial_stakeholders = []
            for stakeholder_name, stakeholder_data in stakeholders.items():
                types = stakeholder_data.get('types', [])
                if field.name in types:
                    initial_stakeholders.append(stakeholder_name)
            field.initial = ','.join(initial_stakeholders)
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
        form = SimilarityTypeForm(initial={
            'similarity': request.session.get('custom_similarity_parameter', '')
        })
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
    original_name = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
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


@csrf_exempt
def node_update(request):
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
            if data.get('custom'):
                similarities.append('custom')
            stakeholders[data['name']] = {
                'interact': int(data['interact']),
                'collaborate': int(data['collaborate']),
                'similarities': similarities,
            }
            if data['name'] != data['original_name']:
                try:
                    del stakeholders[data['original_name']]
                except KeyError:
                    # adding new node
                    pass
            request.session['stakeholders'] = stakeholders
            return JsonResponse({
                'stakeholders': stakeholders,
            })


@csrf_exempt
def node_delete(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        stakeholders = request.session.get('stakeholders', {})
        try:
            del stakeholders[name]
        except KeyError:
            pass
        request.session['stakeholders'] = stakeholders
        return JsonResponse({
            'stakeholders': stakeholders,
        })


@csrf_exempt
def map_save(request):
    map_session = request.session.get('organization')
    if map_session:
        stakeholders = request.session['stakeholders']
        if map_session.get('id'):
            m = Map.objects.get(id=map_session['id'])
            m.stakeholders = stakeholders
            m.save()
        else:
            m = Map.objects.create(**{
                'name': map_session['name'],
                'workshop': request.session.get('workshop'),
                'is_own': map_session['is_own'],
                'sector': get_object_or_404(Sector, id=map_session['sector']),
                'size': map_session['size'],
                'purpose': map_session.get('purpose'),
                'stakeholders': stakeholders,
                'own_parameter': request.session.get('custom_similarity_parameter'),
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
    similarity_type = kwargs.get('similarity_type')
    stakeholders = kwargs.get('stakeholders', {})
    nodes = []
    similars = []
    for name, data in stakeholders.items():
        similarities = data.get('similarities', [])
        icon_prefix = get_node_icon_prefix(similarities)
        node = {
            'label': name,
            'image': static(NODE_ICON_NAME % icon_prefix),
            'similarities': list(icon_prefix),
        }
        nodes.append(node)
        if similarity_type in similarities:
            similars.append(name)
    page_description = kwargs.get('description')
    if page_description:
        kwargs['description'] = page_description % {
            'custom_similarity_parameter': request.session.get('custom_similarity_parameter', '#')
        }
    kwargs.update({
        'nodes': nodes,
        'similars': similars,
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
            'similarity_type': 'values',
            'similarity_icon': 'a',
        },
    },
    {
        'view': picker_view,
        'context': {
            'similarity_type': 'working',
            'similarity_icon': 'c',
        },
    },
    {
        'view': picker_view,
        'context': {
            'similarity_type': 'resources',
            'similarity_icon': 'd',
        },
    },
    {
        'view': ring_view,
        'context': {
            'layout': ring_layout,
        },
    },
    {
        'view': add_custom_similarity,
    },
    {
        'view': picker_view,
        'context': {
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
    if page_no == 0:
        # last page shortcut
        page_no = len(PAGES)
    try:
        page = PAGES[page_no-1]
    except IndexError:
        raise Http404
    request.session['last_page_no'] = page_no
    if workshop_slug:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        request.session['workshop'] = workshop.name
    next_page, prev_page = None, None
    context = page.get('context', {})
    if not context.get('form'):
        next_page = page_no + 1
        if next_page > len(PAGES):
            next_page = None
    if page_no > 1:
        prev_page = page_no - 1
    page_info = PageInfo.objects.filter(page=str(page_no)).first()
    if page_info:
        if request.session.get('organization') and request.session['organization'].get('name'):
            organization_name = request.session['organization']['name']
        else:
            organization_name = None
        context.update({
            'title': page_info.title,
            'description': page_info.description % {
                'organization_name': organization_name
            },
        })
    context.update({
        'stakeholders': request.session.get('stakeholders', {}),
        'page_no': page_no,
        'next_page': next_page,
        'prev_page': prev_page,
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
