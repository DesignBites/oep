
def user_context(request):
    return {
        'workshop': request.session.get('workshop'),
        'stakeholders': request.session.get('stakeholders', {}),
        'organization': request.session.get('organization', {}),
        'custom_similarity_parameter': request.session.get('custom_similarity_parameter'),
        'last_page_no': request.session.get('last_page_no'),
        'terms_ok': request.session.get('terms_ok', False),
    }
