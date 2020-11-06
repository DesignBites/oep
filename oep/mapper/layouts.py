import networkx as nx
from collections import defaultdict
from django.templatetags.static import static


"""
stakeholders = {
    StakeholderName: {
        types: [customer | supplier | collaborator | supporter | extra]
        similarities: [values | working | resources | user_defined]
        interact: 1-3
        collaborate: 1-3
    }
}
"""

SIMILARITY_CONNECTION_ICONS = {
    'values': 'a',
    'working': 'b',
    'resources': 'c',
}


def get_node_icon_prefix(similarities):
    letters = []
    for similarity in similarities:
        letter = SIMILARITY_CONNECTION_ICONS.get(similarity)
        if letter:
            letters.append(letter)
    return ''.join(sorted(letters))


NODE_ICON_NAME = 'nodes/%s_w.png'


def circular_layout(stakeholders):
    positions = [
        (round(x, 2), round(y, 2))
        for x, y in nx.circular_layout(
            list(range(len(stakeholders))),
            scale=1,
        ).values()
    ]
    nodes = []
    i = 1
    for name in stakeholders.keys():
        x, y = positions.pop()
        node = {
            'id': i,
            'label': name,
            'x': x,
            'y': y,
            'size': 3,
            'color': '#f00',
        }
        nodes.append(node)
        i += 1
    return {
        'nodes': nodes,
        'edges': [],
    }


EDGE_TYPES = {
    1: 'dotted',
    2: 'dashed',
    3: 'line',
}


def ring_layout(stakeholders):
    nodes_by_interaction = defaultdict(list)
    for stakeholder_name, data in stakeholders.items():
        if data.get('interact'):
            nodes_by_interaction[data['interact']] = stakeholder_name
    positions = [
        (round(x, 2), round(y, 2))
        for x, y in nx.circular_layout(
            list(range(len(stakeholders))),
            scale=1,
        ).values()
    ]
    nodes = [{
        'id': 0,
        'label': 'You',
        'x': 0,
        'y': 0,
        'size': 10,
        'color': '#f00',
        'type': 'square',
    }]
    edges = []
    i = 1
    for name, data in stakeholders.items():
        if 'interact' in data:
            x, y = positions.pop()
            node = {
                'id': i,
                'label': name,
                'x': x * ((4 - data['interact']) ** 1.4) * 55,
                'y': y * ((4 - data['interact']) ** 1.4) * 55,
                'size': 10,
                'color': '#990',
                'image': {},
            }
            icon_prefix = get_node_icon_prefix(data.get('similarities', []))
            if icon_prefix:
                node['image'] = {
                    'url': static(NODE_ICON_NAME % icon_prefix),
                    'scale': 2,
                    'clip': 2,
                }
            nodes.append(node)
            edges.append({
                'id': 'e%s' % i,
                'source': 0,
                'target': i,
                'size': 2,
                'label': '',
                'color': '#ccc',
                'type': EDGE_TYPES[stakeholders[name]['collaborate']],
            })
            i += 1
    return {
        'nodes': nodes,
        'edges': edges,
    }
