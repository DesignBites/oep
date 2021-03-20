
def user_context(request):
    organization = request.session.get('organization', {})
    organization_name = organization and organization['name']  # to correctly access the name in the template
    return {
        'workshop': request.session.get('workshop'),
        'stakeholders': request.session.get('stakeholders', {}),
        'organization': organization,
        'organization_name': organization_name,
        'custom_similarity_parameter': request.session.get('custom_similarity_parameter'),
        'last_page_no': request.session.get('last_page_no'),
        'terms_ok': request.session.get('terms_ok', False),
    }
