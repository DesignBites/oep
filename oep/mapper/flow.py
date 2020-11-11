from django import forms
from .models import Sector, StakeholderType
from .layouts import circular_layout, ring_layout, venn_layout, suggest_layout


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
        stakeholders = {}
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


class SimilarityTypeForm(forms.Form):
    similarity = forms.CharField(
        label='What is a key parameter for you?',
        help_text='In other words, which other professional, or personal, characteristic '
                  'is important to you to describe your relationships with?',
        required=False,
    )


# the flow
PAGES = [
    {
        'template': 'mapper/form.html',
        'context': {
            'description': 'Let’s get you set up. To support you in identifying and selecting potential collaborators, '
                           'let’s start by getting to know your organisation or team.',
            'form': OrganisationForm,
        },
    },
    {
        'template': 'mapper/map.html',
        'context': {
            'description': '<p>Congratulations, you successfully created your stakeholder map!</p>'
                           '<p>It’s looking rather empty here though, are you ready to add some key stakeholders?</p>',
        },
    },
    {
        'view': 'add_stakeholder_view',
        'context': {
            'title': 'Add stakeholders',
            'description': "Let's start by adding some usual suspects. "
                           "Try to name at least three key stakeholders per question. "
                           "Separate stakeholders with commas, press tab to move to the next question.",
            'form': StakeholderForm,
            'form_kwargs': {'batch_no': 1}
        },
    },
    {
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
            'form': StakeholderForm,
            'form_kwargs': {'batch_no': 2}
        },
    },
    {
        'template': 'mapper/map.html',
        'context': {
            'description': "<p>Awesome, look at all your stakeholders floating around you!</p>"
                           "<p>I’m sure you relate to them in different ways though, "
                           "are you ready to describe the relations to these stakeholders?</p>",
            'graph_layout': circular_layout,
        },
    },
    {
        'template': 'mapper/form.html',
        'context': {
            'title': 'Add stakeholders',
            'description': "Let's start by adding some usual suspects. "
                           "Try to name at least three key stakeholders per question. "
                           "Separate stakeholders with commas, press tab to move to the next question.",
            'form': StakeholderForm,
            'form_kwargs': {'batch_no': 1}
        },
    },
    {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of values',
            'description': "Let's start by indicating who of these key stakeholders are more similar to you. "
                           "For each stakeholder, indicate whether you feel their values, "
                           "ways of working, and resources and skills are similar to you.<br>"
                           "First, select the stakeholders that have similar <strong>values</strong>.",
            'similarity_type': 'values',
            'graph_layout': circular_layout,
            'similarity_icon': 'a',
        },
    },
    {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of ways of working',
            'description': "Now, select the stakeholders that have similar <strong>ways of working</strong>.",
            'similarity_type': 'working',
            'graph_layout': circular_layout,
            'similarity_icon': 'b',
        },
    },
    {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of resources and skills',
            'description': "Lastly, select the stakeholders that have similar <strong>resources and skills</strong>.",
            'similarity_type': 'resources',
            'graph_layout': circular_layout,
            'similarity_icon': 'c',
        },
    },
    {
        'template': 'mapper/picker.html',
        'context': {
            'title': 'Similarity of a parameter of your choice',
            'description': "<p>You can also create your own parameter to compare stakeholders with.</p>",
            'similarity_type': 'user_defined',
            'similarity_type_form': SimilarityTypeForm(),
            'graph_layout': circular_layout,
            'similarity_icon': 'd',
        },
    },
    {
        'template': 'mapper/grid.html',
        'batch': 1,
        'context': {
            'title': 'Frequency and depth of contact',
            'description': "Now select the stakeholders and tap on the right grid to indicate how much you interact, "
                           "and collaborate creatively together.",
        },
    },
    {
        'template': 'mapper/ring.html',
        'context': {
            'description': "<p>Awesome, you now have a stakeholder map.</p>"
                           "<p>You can already play with the filters and different visualisations to reveal "
                           "potential collaborators based on your similarity.</p>"
                           "<p>You can also edit or delete stakeholders by clicking on them.</p>"
                           "<p>There are more stakeholders to add though, are you ready to expand your network?</p>",
            'graph_layout': ring_layout,
        },
    },
    {
        'template': 'mapper/venn.html',
        'context': {
            'graph_layout': venn_layout,
        },
    },
    {
        'template': 'mapper/suggest.html',
        'context': {
            'graph_layout': suggest_layout,
            'modal': 'modalTerms',
        },
    },
]

