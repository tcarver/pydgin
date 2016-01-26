''' Marker page view. '''
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings
from elastic.aggs import Agg, Aggs
from elastic.result import Document
from elastic.exceptions import SettingsError
import logging
from marker.document import MarkerDocument


logger = logging.getLogger(__name__)


def ld_search(request):
    context = {}
    return render(request, 'marker/ld_search.html', context,
                  content_type='text/html')


def marker_page(request, marker):
    ''' Renders a marker page. '''
    if marker is None:
        messages.error(request, 'No marker name given.')
        raise Http404()

    fields = ['id', 'rscurrent'] if marker.startswith("rs") else ['name']
    sub_agg = Agg('top_hits', 'top_hits', {"size": 15})
    aggs = Aggs(Agg("types", "terms", {"field": "_type"}, sub_agg=sub_agg))
    query = ElasticQuery(Query.query_string(marker, fields=fields))
    elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER'), aggs=aggs, size=0)
    res = elastic.search(obj_document=MarkerDocument)
    if res.hits_total >= 1:
        types = getattr(res.aggs['types'], 'buckets')
        marker_doc = None
        ic_docs = []
        history_docs = []
        for doc_type in types:
            hits = doc_type['top_hits']['hits']['hits']
            for hit in hits:
                doc = MarkerDocument(hit)
                if 'marker' == doc_type['key']:
                    marker_doc = doc
                elif 'immunochip' == doc_type['key']:
                    ic_docs.append(doc)
                elif 'rs_merge' == doc_type['key']:
                    history_docs.append(doc)

        criteria = {}
        if marker_doc is not None:
            #if ElasticSettings.idx('CRITERIA') is not None:
            #    criteria = views.get_criteria([marker_doc], 'marker', 'id', 'MARKER')
            marker_doc.marker_build = _get_marker_build(ElasticSettings.idx('MARKER'))

        context = {
            'features': [marker_doc],
            'old_dbsnp_docs': _get_old_dbsnps(marker),
            'ic': ic_docs,
            'history': history_docs,
            'criteria': criteria
        }
        return render(request, 'marker/marker.html', context,
                      content_type='text/html')
    elif res.hits_total == 0:
        messages.error(request, 'Marker '+marker+' not found.')
        raise Http404()


def marker_page_params(request):
    ''' Renders a marker page from GET query params. '''
    query_dict = request.GET
    return marker_page(request, query_dict.get("m"))


def _get_old_dbsnps(marker):
    ''' Get markers from old versions of DBSNP. Assumes the index key is
    prefixed by 'MARKER_'. '''
    old_dbsnps_names = sorted([ElasticSettings.idx(k) for k in ElasticSettings.getattr('IDX').keys()
                               if 'MARKER_' in k], reverse=True)
    old_dbsnp_docs = []
    if len(old_dbsnps_names) > 0:
        search_query = ElasticQuery(Query.query_string(marker, fields=['id', 'rscurrent']))
        for idx_name in old_dbsnps_names:
            elastic2 = Search(search_query=search_query, idx=idx_name, idx_type='marker')
            docs = elastic2.search().docs
            if len(docs) > 0:
                old_doc = docs[0]
                old_doc.marker_build = _get_marker_build(idx_name)
                old_dbsnp_docs.append(old_doc)
    return old_dbsnp_docs


def _get_marker_build(idx_name):
    ''' Get the marker build as defined in the settings. '''
    try:
        idx_key = ElasticSettings.get_idx_key_by_name(idx_name)
        return ElasticSettings.get_label(idx_key, label='build')
    except (KeyError, SettingsError, TypeError):
        logger.error('Marker build not identified from ELASTIC settings.')
        return ''
