''' Template tags for the search engine app. '''
from django import template
from elastic.elastic_settings import ElasticSettings
from django.utils.datastructures import SortedDict
import collections

register = template.Library()


@register.inclusion_tag('search_engine/search_engine_section.html')
def show_search_engine():
    ''' Template inclusion tag to render search engine form. '''
    return {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}


@register.filter(name='sort')
def listsort(value):
    ''' Sort dict, list and iterable arguments. '''
    if isinstance(value, dict):
        new_dict = SortedDict()
        key_list = value.keys()
        key_list.sort()
        for key in key_list:
            new_dict[key] = value[key]
        return new_dict
    elif isinstance(value, list):
        try:
            new_list = list(value)
            new_list.sort()
            return new_list
        except TypeError:
            # sorting a list of dictionaries?
            if 'key' in value[0]:
                return sorted(value, key=lambda k: k['key'])
            return value
    elif isinstance(value, collections.Iterable):
        return sorted(value)
    return value

listsort.is_safe = True
