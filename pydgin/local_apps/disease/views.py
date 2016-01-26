from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from django.contrib import messages
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings


@ensure_csrf_cookie
def disease_page(request):
    ''' Renders a disease page. '''
    query_dict = request.GET
    disease = query_dict.get("d").lower()
    if disease is None:
        messages.error(request, 'No disease given.')
        raise Http404()
    query = ElasticQuery(Query.terms("code", [disease.split(',')]))
    elastic = Search(query, idx=ElasticSettings.idx('DISEASE', 'DISEASE'), size=5)
    res = elastic.search()
    if res.hits_total == 0:
        messages.error(request, 'Disease(s) '+disease+' not found.')
    elif res.hits_total < 9:
        names = ', '.join([getattr(doc, 'name') for doc in res.docs])
        context = {'diseases': res.docs, 'title': names}
        return render(request, 'disease/disease.html', context, content_type='text/html')
    raise Http404()
