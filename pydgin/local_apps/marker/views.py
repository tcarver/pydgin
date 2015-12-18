''' Marker page view. '''
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render
from elastic.search import ElasticQuery, Search
from elastic.query import Query, BoolQuery
from elastic.elastic_settings import ElasticSettings
from elastic.aggs import Agg, Aggs
from elastic.result import Document
from gene import views
from elastic.exceptions import SettingsError
from django.http.response import JsonResponse
import pyRserve
import logging
import json


logger = logging.getLogger(__name__)


def ld(request):
    query_dict = request.GET
    mid1 = query_dict.get("m1")
    mid2 = query_dict.get("m2")
    window_size = query_dict.get("window_size", 1000000)
    dprime = query_dict.get("dprime", 0.)
    rsq = query_dict.get("rsq", 0.8)
    maf = query_dict.get("maf", False)
    pos = query_dict.get("pos", False)
    dataset = query_dict.get("dataset", "HapMap_CEU_Founders_r23a")
    print(mid2)

    query = ElasticQuery(BoolQuery(must_arr=[Query.term("id", mid1)]), sources=['seqid'])
    elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER', 'MARKER'), size=1)
    seqid = getattr(elastic.search().docs[0], 'seqid')

    conn = pyRserve.connect(host='localhost', port=6311)
    x = conn.r.run(seqid, dataset, mid1, marker2=mid2,
                   window_size=window_size, dprime=dprime,
                   rsq=rsq, maf=maf, position=pos)
    conn.close()

    return JsonResponse(json.loads(str(x)))


def marker_page(request):
    ''' Renders a gene page. '''
    query_dict = request.GET
    marker = query_dict.get("m")
    if marker is None:
        messages.error(request, 'No gene name given.')
        raise Http404()

    fields = ['id', 'rscurrent'] if marker.startswith("rs") else ['name']
    sub_agg = Agg('top_hits', 'top_hits', {"size": 15})
    aggs = Aggs(Agg("types", "terms", {"field": "_type"}, sub_agg=sub_agg))
    query = ElasticQuery(Query.query_string(marker, fields=fields))
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

        criteria = {}
        if marker_doc is not None:
            if ElasticSettings.idx('CRITERIA') is not None:
                criteria = views.get_criteria([marker_doc], 'marker', 'id', 'MARKER')
            marker_doc.marker_build = _get_marker_build(ElasticSettings.idx('MARKER'))

        context = {
            'marker': marker_doc,
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
