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
        new_list = list(value)
        new_list.sort()
        return new_list
    elif isinstance(value, collections.Iterable):
        return sorted(value)
    else:
        return value

listsort.is_safe = True
