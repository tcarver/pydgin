''' Template tags for the disease app. '''
from django import template
from elastic.elastic_settings import ElasticSettings
from elastic.search import ElasticQuery, Search
from elastic.query import Query, BoolQuery
from elastic.result import Document

register = template.Library()


@register.inclusion_tag('disease/disease_bar.html')
def show_disease_bar():
    ''' Template inclusion tag to render disease bar. '''
    query = ElasticQuery(Query.match_all())
    elastic = Search(query, idx=ElasticSettings.idx('DISEASE'), size=50)
    return {'diseases': elastic.search().docs}


@register.inclusion_tag('disease/disease_code.html')
def show_disease(disease, scores):
    ''' Template inclusion tag to render disease bar. '''
    if isinstance(disease, str):
        if disease == 'OD':
            disease = Document({"_source": {"code": "Others", "colour": "grey", "name": "Other Diseases"}})
        else:
            query = ElasticQuery(BoolQuery(should_arr=[Query.term('code', disease.lower()),
                                                       Query.term('name', disease.lower())]))
            disease = Search(query, idx=ElasticSettings.idx('DISEASE'), size=1).search().docs[0]
    score = ''
    if scores != '':
        score = scores[0]
    return {'disease': disease, 'score': score}
