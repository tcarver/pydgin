from django import template
from django.conf import settings

register = template.Library()


@register.filter
def is_list(val):
    ''' Is the value an instance of a list. '''
    return isinstance(val, list)


@register.inclusion_tag('gene/pub_section.html')
def show_pub_section(region):
    ''' Template inclusion tag to render a publication section given a list of PMIDs. '''
    return {'region': region}


@register.inclusion_tag('gene/studies_section.html')
def show_studies_section(region_id):
    ''' Template inclusion tag to render an studies section given a region ID. '''
    return {'region_id': region_id}
