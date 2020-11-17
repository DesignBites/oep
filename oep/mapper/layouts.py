import networkx as nx
from collections import defaultdict
from itertools import combinations
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
        icon_prefix = get_node_icon_prefix(data.get('similarities', []))
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
    #for name in sorted_names:
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
            node = {
                'id': i,
                'label': name,
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
    similarities = ['values', 'working', 'resources']
    center_coordinates = {
        ('values', 'working', 'resources'): [-40, -80],
        ('values', 'working'): [-200, -100],
        ('values', 'resources'): [100, -100],
        ('working', 'resources'): [-40, 120],
        ('values',): [0, -250],
        ('working',): [-250, 80],
        ('resources',): [150, 80],
    }
    venn = defaultdict(list)
    used = []
    for i in range(3, 0, -1):
        for combination in combinations(similarities, i):
            for stakeholder, data in stakeholders.items():
                if len(set(data.get('similarities', [])).intersection(combination)) == i:
                    if not stakeholder in used:
                        venn[combination].append(stakeholder)
                        used.append(stakeholder)
    nodes = []
    i = 1
    for section, stakeholder_list in venn.items():
        positions = [
            (round(x, 2), round(y, 2))
            for x, y in nx.random_layout(
                list(range(len(stakeholders))),
            ).values()
        ]
        center = center_coordinates[section]
        for name in stakeholder_list:
            x, y = positions.pop()
            node = {
                'id': i,
                'label': name,
                'x': center[0] + x * 100,
                'y': center[1] + y * 100,
                'size': 10,
                'color': '#990',
                'image': {},
            }
            icon_prefix = get_node_icon_prefix(stakeholders[name].get('similarities', []))
            if icon_prefix:
                node['image'] = {
                    'url': static(NODE_ICON_NAME % icon_prefix),
                    'scale': 3,
                    'clip': 3,
                }
            nodes.append(node)
            i += 1
    return {
        'nodes': nodes,
    }


def suggest_layout(stakeholders):
    lists = defaultdict(list)
    for stakeholder, data in stakeholders.items():
        if len(data.get('similarities', [])) >= 2:
            if data.get('interact', 0) >= 2:
                if data.get('collaborate', 0) <= 2:
                    lists[1].append(stakeholder)
        if len(data.get('similarities', [])) == 1:
            if data.get('interact', 0) <= 2:
                if data.get('collaborate', 0) == 1:
                    lists[2].append(stakeholder)
    nodes = defaultdict(list)
    for key, l in lists.items():
        positions = [
            (round(x, 2), round(y, 2))
            for x, y in nx.random_layout(
                list(range(len(l))),
            ).values()
        ]
        i = 1
        for name in l:
            x, y = positions.pop()
            node = {
                'id': i,
                'label': name,
                'x': x * 300 - 150,
                'y': y * 300 - 150,
                'size': 15,
                'color': '#990',
                'type': 'diamond',
                'image': {},
            }
            icon_prefix = get_node_icon_prefix(stakeholders[name].get('similarities', []))
            if icon_prefix:
                node['image'] = {
                    'url': static(NODE_ICON_NAME % icon_prefix),
                    'scale': 3,
                    'clip': 3,
                }
            nodes[key].append(node)
            i += 1
    return {
        'nodes': dict(nodes),
    }
