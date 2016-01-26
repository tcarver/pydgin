from django import template
from django.conf import settings

register = template.Library()


@register.filter
def db_link(db):
    ''' Look up a URL for a given database. '''
    settings
    db_names = settings.URL_LINKS.keys()
    if db.lower() in db_names:
        return settings.URL_LINKS[db]
    return ""


@register.filter
def is_list(val):
    ''' Is the value an instance of a list. '''
    return isinstance(val, list)


@register.inclusion_tag('sections/pub.html')
def show_pub_section(gene):
    ''' Template inclusion tag to render a publication section given a
    list of PMIDs. '''
    return {'feature': gene}
