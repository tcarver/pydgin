from django import template

register = template.Library()


@register.inclusion_tag('auth_test/render_color_page.html')
def pages_to_display(request):
    # check perms and display pages
    # default page read by all
    page_sections = ['green']
    if request.user.is_authenticated():

        # check if user is in group 'PYDGIN_ADMIN'
        if request.user.groups.filter(name='PYDGIN_ADMIN').exists():
            page_sections.append('red')

        # check if user is superuser
        if request.user.is_superuser:
            page_sections.append('black')

        # check perms
        if request.user.has_perm('auth_test.can_read'):
            page_sections.append('blue')
        if request.user.has_perm('auth_test.can_read_curate'):
            page_sections.append('yellow')

    return {'pages_to_render': page_sections}
