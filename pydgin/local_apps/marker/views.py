
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings
from elastic.aggs import Agg, Aggs
from elastic.result import Document


def marker_page(request):
    ''' Renders a gene page. '''
    query_dict = request.GET
    marker = query_dict.get("m")
    if marker is None:
        messages.error(request, 'No gene name given.')
        raise Http404()

    sub_agg = Agg('top_hits', 'top_hits', {"size": 15})
    aggs = Aggs(Agg("types", "terms", {"field": "_type"}, sub_agg=sub_agg))
    query = ElasticQuery(Query.query_string(marker, fields=['id', 'rscurrent']))
    elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER'), aggs=aggs, size=0)
    res = elastic.search()
    if res.hits_total >= 1:
        types = getattr(res.aggs['types'], 'buckets')
        marker_doc = None
        ic_docs = []
        history_docs = []
        for doc_type in types:
            hits = doc_type['top_hits']['hits']['hits']
            for hit in hits:
                doc = Document(hit)
                if 'marker' == doc_type['key']:
                    marker_doc = doc
                elif 'immunochip' == doc_type['key']:
                    ic_docs.append(doc)
                elif 'rs_merge' == doc_type['key']:
                    history_docs.append(doc)

        context = {'marker': marker_doc, 'ic': ic_docs, 'history': history_docs}
        return render(request, 'marker/marker.html', context,
                      content_type='text/html')
    elif res.hits_total == 0:
        messages.error(request, 'Marker '+marker+' not found.')
        raise Http404()
