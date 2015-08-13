''' Template tags for the search engine app. '''
from django import template
from elastic.elastic_settings import ElasticSettings
import collections

register = template.Library()


@register.inclusion_tag('search_engine/search_engine_section.html')
def show_search_engine():
    ''' Template inclusion tag to render search engine form. '''
    return {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}


@register.filter(name='sort')
def listsort(value):
    ''' Sort list and iterable arguments. '''
    if isinstance(value, list):
        try:
            new_list = list(value)
            new_list.sort()
            return new_list
        except TypeError:
            # sorting a list of dictionaries?
            if 'key' in value[0]:
                return sorted(value, key=lambda k: k['key'])
    elif isinstance(value, collections.Iterable):
        return sorted(value)
    return value

listsort.is_safe = True
