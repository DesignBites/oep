import networkx as nx
from collections import defaultdict
from itertools import combinations
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


def venn_layout(stakeholders):
    similarities = ['values', 'working', 'resources']
    center_coordinates = {
        ('values', 'working', 'resources'): [0, 0],
        ('values', 'working'): [-50, 50],
        ('values', 'resources'): [50, 50],
        ('working', 'resources'): [0, -70],
        ('values',): [0, 150],
        ('working',): [-100, -100],
        ('resources',): [100, -100],
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
                'x': center[0] + x * 80,
                'y': center[1] + y * 80,
                'size': 10,
                'color': '#990',
                'image': {},
            }
            icon_prefix = get_node_icon_prefix(stakeholders[name].get('similarities', []))
            if icon_prefix:
                node['image'] = {
                    'url': static(NODE_ICON_NAME % icon_prefix),
                    'scale': 2,
                    'clip': 2,
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
            if data.get('interact', 0) <= 3:
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
                'x': x * 10,
                'y': y * 10,
                'size': 10,
                'color': '#990',
                'type': 'diamond',
                'image': {},
            }
            icon_prefix = get_node_icon_prefix(stakeholders[name].get('similarities', []))
            if icon_prefix:
                node['image'] = {
                    'url': static(NODE_ICON_NAME % icon_prefix),
                    'scale': 2,
                    'clip': 2,
                }
            nodes[key].append(node)
            i += 1
    return {
        'nodes': dict(nodes),
    }
