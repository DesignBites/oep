
def user_context(request):
    return {
        'workshop': request.session.get('workshop'),
        'stakeholders': request.session.get('stakeholders'),
        'map': request.session.get('map'),
        'terms_ok': request.session.get('terms_ok', False),
        'custom_similarity_parameter': request.session.get('custom_similarity_parameter'),
    }
