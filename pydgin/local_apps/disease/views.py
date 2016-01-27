from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from django.contrib import messages
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings
from disease.document import DiseaseDocument


@ensure_csrf_cookie
def disease_page(request, disease):
    ''' Renders a disease page. '''
    disease = disease.lower()
    if disease is None:
        messages.error(request, 'No disease given.')
        raise Http404()
    query = ElasticQuery(Query.terms("code", [disease.split(',')]))
    elastic = Search(query, idx=ElasticSettings.idx('DISEASE', 'DISEASE'), size=5)
    res = elastic.search(obj_document=DiseaseDocument)
    if res.hits_total == 0:
        messages.error(request, 'Disease(s) '+disease+' not found.')
    elif res.hits_total < 9:
        names = ', '.join([getattr(doc, 'name') for doc in res.docs])
        context = {'features': res.docs, 'title': names}
        return render(request, 'feature.html', context, content_type='text/html')
    raise Http404()


def disease_page_params(request):
    ''' Renders a disease page from GET query params. '''
    query_dict = request.GET
    return disease_page(request, query_dict.get("d"))
