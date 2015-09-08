''' Template tags for the search engine app. '''
from django import template
from elastic.elastic_settings import ElasticSettings
from elastic.result import Document
from django.conf import settings
import re

register = template.Library()


@register.inclusion_tag('search_engine/search_engine_section.html')
def show_search_engine():
    ''' Template inclusion tag to render search engine form. '''
    return {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}


HIGHLIGHT_HTML_TAGS = ['<strong>', '</strong>', '<div class="col-md-2 text-right">',
                       '<div class="col-md-10">', '<div class="row">', '</div>']


@register.filter
def doc_highlight(doc):
    ''' Gets the highlighted section and split into fragments for parsing
    html tags as safe. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID

    html = ''
    if doc.highlight() is None:
        return ''
    for key, values in doc.highlight().items():
        html += \
           '<div class="row"><div class="col-md-2 text-right"><strong>%s</strong></div><div class="col-md-10">' % key
        for value in values:
            html += '%s ' % value
        html += '</div></div>'

    split_tags = '|'.join(HIGHLIGHT_HTML_TAGS)
    html_fragments = re.split('('+split_tags+')', html)
    return html_fragments


@register.filter
def doc_highlight_keys(doc):
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    if doc.highlight() is None:
        return ''
    return doc.highlight().keys()


@register.filter
def doc_highlight_html_tags(doc):
    return HIGHLIGHT_HTML_TAGS
