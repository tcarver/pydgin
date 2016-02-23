''' Marker page view. '''
import logging

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from elastic.exceptions import SettingsError
from elastic.query import Query
from elastic.search import ElasticQuery, Search

from core.document import PydginDocument
from core.views import SectionMixin, CDNMixin


logger = logging.getLogger(__name__)


class MarkerView(CDNMixin, SectionMixin, TemplateView):
    ''' Renders a marker page. '''
    template_name = "marker/index.html"

    def get_context_data(self, **kwargs):
        context = super(MarkerView, self).get_context_data(**kwargs)
        return MarkerView.get_marker(self.request, kwargs['marker'], context)

    @classmethod
    def get_marker(cls, request, marker, context):
        if marker is None:
            messages.error(request, 'No marker name given.')
            raise Http404()

        fields = ['id', 'rscurrent'] if marker.startswith("rs") else ['name']
        sub_agg = Agg('top_hits', 'top_hits', {"size": 15})
        aggs = Aggs(Agg("types", "terms", {"field": "_type"}, sub_agg=sub_agg))
        query = ElasticQuery(Query.query_string(marker, fields=fields))
        elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER'), aggs=aggs, size=0)
        res = elastic.search()
        title = ''
        if res.hits_total >= 1:
            types = getattr(res.aggs['types'], 'buckets')
            marker_doc = None
            ic_docs = []
            history_docs = []
            for doc_type in types:
                hits = doc_type['top_hits']['hits']['hits']
                for hit in hits:
                    doc = PydginDocument.factory(hit)
                    title = doc.get_name()

                    if 'marker' == doc_type['key']:
                        marker_doc = doc
                    elif 'immunochip' == doc_type['key']:
                        ic_docs.append(doc)
                    elif 'rs_merge' == doc_type['key']:
                        history_docs.append(doc)

            if marker_doc is not None:
                marker_doc.marker_build = _get_marker_build(ElasticSettings.idx('MARKER'))

            # context['marker'] = marker_doc
            context['features'] = [marker_doc]
            context['old_dbsnp_docs'] = _get_old_dbsnps(marker)
            context['ic'] = ic_docs
            context['history'] = history_docs
            context['title'] = title
            return context
        elif res.hits_total == 0:
            messages.error(request, 'Marker '+marker+' not found.')
            raise Http404()


def _get_old_dbsnps(marker):
    ''' Get markers from old versions of DBSNP. Assumes the index key is
    prefixed by 'MARKER_\d+'. eg: MARKER_138'''
    old_dbsnps_names = sorted([ElasticSettings.idx(k) for k in ElasticSettings.getattr('IDX').keys()
                               if 'MARKER_\d+' in k], reverse=True)
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


class MarkerViewParams(MarkerView):
    ''' Renders a marker page. '''
    def get_context_data(self, **kwargs):
        return super(MarkerViewParams, self).get_context_data(marker=self.request.GET.get('m'), **kwargs)


class JSTestView(CDNMixin, TemplateView):
    ''' Renders a marker page. '''
    template_name = "js_test/ld.html"

    def get_context_data(self, **kwargs):
        context = super(JSTestView, self).get_context_data(**kwargs)
        if not (settings.DEBUG or settings.TESTMODE):
            raise Http404()
        return context
