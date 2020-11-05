import networkx as nx


"""
stakeholders = {
    StakeholderName: {
        types: [customer | supplier | collaborator | supporter]
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


def get_icon_name(stakeholder):
    letters = []
    for similarity in stakeholder.get('similarities', []):
        letter = SIMILARITY_CONNECTION_ICONS.get(similarity)
        if letter:
            letters.append(letter)
    return ''.join(sorted(letters))


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
