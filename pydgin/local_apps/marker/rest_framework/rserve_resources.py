from elastic.search import Search, ElasticQuery
from elastic.query import Query, BoolQuery
from elastic.elastic_settings import ElasticSettings
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response
from django.conf import settings
from django.http.response import Http404
import pyRserve
import json
from elastic.rest_framework.elastic_obj import ElasticObject


class LDFilterBackend(OrderingFilter, DjangoFilterBackend):
    ''' Extend L{DjangoFilterBackend} for filtering elastic resources. '''

    def filter_queryset(self, request, queryset, view):
        ''' Override this method to request just the documents required from Rserve. '''
        try:
            filterable = getattr(view, 'filter_fields', [])
            filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])

            mid1 = filters.get('m1')
            if mid1 is None or mid1 == '':
                return [ElasticObject(initial={'error': 'No marker ID provided.'})]

            dataset = filters.get('dataset', 'EUR').replace('-', '')
            mid2 = filters.get("m2")
            window_size = int(filters.get('window_size', 1000000))
            dprime = filters.get("dprime", 0.)
            rsq = filters.get("rsq", 0.8)
            maf = filters.get("maf", False)
            if maf:
                maf = True
            build_version = filters.get("build", 'GRCh38').lower()
            pos = filters.get("pos", False)
            if pos:
                pos = True

            query = ElasticQuery(BoolQuery(must_arr=[Query.term("id", mid1)]), sources=['seqid', 'start'])
            elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER', 'MARKER'), size=1)
            doc = elastic.search().docs[0]
            seqid = getattr(doc, 'seqid')

            rserve = getattr(settings, 'RSERVE')
            conn = pyRserve.connect(host=rserve.get('HOST'), port=rserve.get('PORT'))
            ld_str = conn.r.ld_run(dataset, seqid, mid1, marker2=mid2,
                                   window_size=window_size, dprime=dprime,
                                   rsq=rsq, maf=maf, position=pos, build_version=build_version)
            ld_str = ld_str.replace('D.prime', 'dprime').replace('R.squared', 'rsquared')
            conn.close()

            return [ElasticObject(initial=json.loads(str(ld_str)))]
        except (TypeError, ValueError, IndexError, ConnectionError):
            raise Http404


class ListLDMixin(object):
    ''' List queryset. '''
    filter_backends = [LDFilterBackend, ]

    def get_queryset(self):
        return None

    def list(self, request, m1='rs2476601', *args, **kwargs):
        ''' Retrieve a list of documents. '''
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class RetrieveLDMixin(object):
    ''' Retrieve an instance. '''
    def retrieve(self, request, *args, **kwargs):
        ''' Retrieve a document instance. '''
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        mid1 = self.kwargs[self.lookup_url_kwarg]
        dataset = 'EUR'
        try:
            query = ElasticQuery(BoolQuery(must_arr=[Query.term("id", mid1)]), sources=['seqid', 'start'])
            elastic = Search(search_query=query, idx=ElasticSettings.idx('MARKER', 'MARKER'), size=1)
            doc = elastic.search().docs[0]
            rserve = getattr(settings, 'RSERVE')
            conn = pyRserve.connect(host=rserve.get('HOST'), port=rserve.get('PORT'))
            ld_str = conn.r.ld_run(dataset, getattr(doc, 'seqid'), mid1)
            ld_str = ld_str.replace('D.prime', 'dprime').replace('R.squared', 'rsquared')
            conn.close()
            return ElasticObject(initial=json.loads(str(ld_str)))
        except (TypeError, ValueError, IndexError, ConnectionError):
            raise Http404
