from django.shortcuts import render
from oep.network.models import RELATION_GROUPS


def graph(request):
    return render(request, 'network/graph.html', {
        'relation_groups': RELATION_GROUPS,
    })
