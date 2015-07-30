from django import template
from elastic.elastic_settings import ElasticSettings

register = template.Library()


@register.inclusion_tag('search_engine/search_engine_section.html')
def show_search_engine():
    ''' Template inclusion tag to render a gene section given a
    chado gene feature. '''
    return {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}
