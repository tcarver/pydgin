''' Template tags for the pydgin project. '''
from django import template
from elastic.elastic_settings import ElasticSettings
from elastic.search import ElasticQuery, Search
from elastic.query import Query

register = template.Library()


@register.inclusion_tag('disease/disease_bar.html')
def show_disease():
    ''' Template inclusion tag to render disease bar. '''
    query = ElasticQuery(Query.match_all())
    elastic = Search(query, idx=ElasticSettings.idx('DISEASE'), size=50)
    return {'diseases': elastic.search().docs}
