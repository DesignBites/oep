from random import shuffle
import networkx as nx
from collections import defaultdict
from django.templatetags.static import static


"""
stakeholders = {
    StakeholderName: {
        types: [customer | supplier | collaborator | supporter | extra]
        similarities: [values | working | resources | custom]
        interact: 1-3
        collaborate: 1-3
    }
}
"""

SIMILARITY_CONNECTION_ICONS = {
    'values': 'a',
    'working': 'c',
    'resources': 'd',
}


def get_node_icon_prefix(similarities):
    letters = []
    if similarities:
        similarities = list(set(similarities))
        for similarity in similarities:
            letter = SIMILARITY_CONNECTION_ICONS.get(similarity)
            if letter:
                letters.append(letter)
            else:
                letters.append('b')  # custom (user defined) similarity
        return ''.join(sorted(letters))
    else:
        return 'O'


NODE_ICON_NAME = 'nodes/%s.png'


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
    for name, data in stakeholders.items():
        x, y = positions.pop()
        similarities = data.get('similarities', [])
        icon_prefix = get_node_icon_prefix(similarities)
        node = {
            'id': i,
            'label': name,
            'x': x,
            'y': y,
            'size': 3,
            'color': '#f00',
            'image': {
                'url': static(NODE_ICON_NAME % icon_prefix),
                'scale': 3,
                'clip': 3,
            },
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
        'image': {
            'url': static(NODE_ICON_NAME % 'O'),
            'scale': 3,
            'clip': 3,
        },
    }]
    # calculate the center population
    center_population = 0
    for name, data in stakeholders.items():
        if data.get('interact') == 3:
            center_population += 1
    central_size = center_population > 10 and 9 or 10
    # sort by proximity
    #sorted_names = sorted(stakeholders, key=lambda x: (stakeholders[x]['interact']), reverse=True)
    edges = []
    i = 1
    # for name in sorted_names:
    for name in stakeholders.keys():
        data = stakeholders[name]
        if 'interact' in data:
            # 4 levels of proximity; 2 for the most inner circle
            if data['interact'] == 3:
                proximity = [1, 1.9][i % 2]
            elif data['interact'] == 2:
                proximity = 3.5
            else:  # 1
                proximity = 5
            x, y = positions.pop()
            icon_prefix = get_node_icon_prefix(data.get('similarities', []))
            label = name
            if data['interact'] == 3:
                if len(name) > 6:
                    label = name[:4] + '…'
            else:
                if len(name) > 12:
                    label = name[:10] + '…'
            node = {
                'id': i,
                'label': label,
                'fullLabel': name,
                'shortLabel': label,
                'x': x * proximity * 55,
                'y': y * proximity * 55,
                'size': data['interact'] == 3 and central_size or 10,
                'color': '#990',
                'image': {
                    'url': static(NODE_ICON_NAME % icon_prefix),
                    'scale': 3,
                    'clip': 3,
                },
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


def venn_layout(stakeholders):
    similarity_values = {
        'values': 8,
        'working': 4,
        'resources': 2,
        'custom': 1,
    }
    venn = {}
    for stakeholder, data in stakeholders.items():
        cell = 0
        similarities = data.get('similarities', [])
        for similarity in similarities:
            cell += similarity_values[similarity]
        venn[stakeholder] = {
            'cell': f'{cell:b}'.zfill(4),
            'icon': static(NODE_ICON_NAME % get_node_icon_prefix(similarities)),
        }
    return {
        'venn': venn,
    }


def suggest_layout(stakeholders):
    MAX_QUADRANT_POPULATION = 20
    # (collaborate, interact, similarity count)
    rules = {
        'q1': [
            (1, 1, 4), (1, 1, 3), (1, 2, 4), (1, 2, 3), (1, 1, 2), (1, 2, 2),
        ],
        'q2': [
            (1, 1, 1), (1, 2, 1), (1, 1, 2), (1, 2, 2),
        ],
        'q3': [
            (1, 3, 4), (1, 3, 3), (2, 3, 4), (2, 3, 3), (1, 2, 4), (1, 2, 3),
            (2, 2, 4), (2, 2, 3), (1, 3, 2), (2, 3, 2), (2, 2, 2),
        ],
        'q4': [
            (1, 3, 1), (1, 3, 2), (2, 3, 1), (2, 3, 2), (1, 2, 1), (1, 2, 2), (2, 2, 1), (2, 2, 2),
        ]
    }
    stakeholders_keys = defaultdict(list)
    for name, data in stakeholders.items():
        key = (
            data.get('collaborate'),
            data.get('interact'),
            len(data.get('similarities', [])),
        )
        stakeholders_keys[key].append(name)
    quadrants = defaultdict(list)
    for q in rules.keys():
        for rule in rules[q]:
            matched_stakeholders = stakeholders_keys.get(rule, [])
            shuffle(matched_stakeholders)
            names = matched_stakeholders[:MAX_QUADRANT_POPULATION - len(quadrants[q])]
            for name in names:
                icon_prefix = get_node_icon_prefix(stakeholders[name].get('similarities', []))
                quadrants[q].append({
                    'name': name,
                    'icon': static(NODE_ICON_NAME % icon_prefix),
                })
            if len(quadrants[q]) == MAX_QUADRANT_POPULATION:
                continue
    return {
        'quadrants': dict(quadrants),
        'initial_quadrant_population': 2,
    }
