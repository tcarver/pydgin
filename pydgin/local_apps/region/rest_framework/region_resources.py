''' Define a resource for LD Rserve data to be used in Django REST framework. '''
from django.conf import settings
from django.http.response import Http404
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response

from region.document import DiseaseLocusDocument
from django.contrib import messages
from region import views


class RegionsFilterBackend(OrderingFilter, DjangoFilterBackend):
    ''' Extend L{DjangoFilterBackend} for filtering LD resources. '''

    BUILD_MAP = {
        'hg18': 36,
        'hg19': 37,
        'hg38': 38
    }

    def _get_build(self, build):
        ''' Given the build return the build number as an integer. '''
        for hg, b in RegionsFilterBackend.BUILD_MAP.items():
            if hg == build:
                return b
        return int(build)

    def filter_queryset(self, request, queryset, view):
        ''' Override this method to request feature locations. '''
        try:
            filterable = getattr(view, 'filter_fields', [])
            filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])
            dis = filters.get('disease', 'T1D')
            build = self._get_build(filters.get('build', settings.DEFAULT_BUILD))
            docs = DiseaseLocusDocument.get_disease_loci_docs(dis)
            if len(docs) == 0:
                messages.error(request, 'No regions found for '+dis+'.')

            visible_hits = DiseaseLocusDocument.get_hits([h for r in docs for h in getattr(r, 'hits')])
            regions = []
            for r in docs:
                region = r.get_disease_region(visible_hits, build=build)
                if region is not None:

                    (all_coding, all_non_coding) = views.get_genes_for_region(getattr(r, "seqid"),
                                                                              region['rstart']-500000,
                                                                              region['rstop']+500000)
                    (region_coding, coding_up, coding_down) = views._region_up_down(all_coding, region['rstart'],
                                                                                    region['rstop'])
                    (region_non_coding, non_coding_up, non_coding_down) = \
                        views._region_up_down(all_non_coding, region['rstart'], region['rstop'])
                    region['genes'] = {
                        'upstream': {'coding': [g.doc_id() for g in coding_up],
                                     'non_coding': [g.doc_id() for g in non_coding_up]},
                        'region': {'coding': [g.doc_id() for g in region_coding],
                                   'non_coding': [g.doc_id() for g in region_non_coding]},
                        'downstream': {'coding': [g.doc_id() for g in coding_down],
                                       'non_coding': [g.doc_id() for g in non_coding_down]},
                    }
                    regions.append(region)
            return regions
        except (TypeError, ValueError, IndexError, ConnectionError) as e:
            print(e)
            raise Http404


class ListRegionsMixin(object):
    ''' Get a list of locations for a feature. '''
    filter_backends = [RegionsFilterBackend, ]

    def get_queryset(self):
        return None

    def list(self, request, **kwargs):
        ''' Retrieve a list of documents. '''
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
