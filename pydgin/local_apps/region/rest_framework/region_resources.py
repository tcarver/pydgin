''' Define a resource for LD Rserve data to be used in Django REST framework. '''
from django.conf import settings
from django.http.response import Http404
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response

from region.document import DiseaseLocusDocument
from django.contrib import messages
from region import views
from elastic.search import ElasticQuery, Search
from elastic.query import Query, Filter, RangeQuery, BoolQuery
from elastic.elastic_settings import ElasticSettings
from elastic.result import Document
from gene.document import GeneDocument


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
        ''' Get disease regions. '''
        try:
            filterable = getattr(view, 'filter_fields', [])
            filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])
            dis = filters.get('disease', 'T1D')
            show_genes = filters.get('genes', False)
            show_markers = filters.get('markers', False)

            build = self._get_build(filters.get('build', settings.DEFAULT_BUILD))
            docs = DiseaseLocusDocument.get_disease_loci_docs(dis)
            if len(docs) == 0:
                messages.error(request, 'No regions found for '+dis+'.')

            visible_hits = DiseaseLocusDocument.get_hits([h for r in docs for h in getattr(r, 'hits')])
            regions = []
            all_markers = []
            all_genes = []
            ens_all_cand_genes = []
            for r in docs:
                region = r.get_disease_region(visible_hits, build=build)
                if region is not None:
                    ens_all_cand_genes.extend(region['ens_cand_genes'])
                    all_markers.extend(region['markers'])
                    for h in r.hit_docs:
                        if h.disease is not None:
                            region['all_diseases'].append(h.disease)

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
                    all_genes.extend(region['genes']['region']['coding'])
                    all_genes.extend(region['genes']['region']['non_coding'])
                    regions.append(region)

            # look for pleiotropy by looking for diseases for the markers in IC_STATS and other study hits
            stats_query = ElasticQuery.filtered(Query.terms("marker", all_markers),
                                                Filter(RangeQuery("p_value", lte=5E-08)))
            stats_docs = Search(stats_query, idx=ElasticSettings.idx("IC_STATS"), size=len(all_markers)).search().docs
            meta_response = Search.elastic_request(ElasticSettings.url(), ElasticSettings.idx("IC_STATS") + '/_mapping',
                                                   is_post=False)
            # get ensembl to gene symbol mapping for all candidate genes
            for region in regions:
                # add diseases from IC/GWAS stats
                (study_ids, region['marker_stats']) = views._process_stats(stats_docs, region['markers'], meta_response)
                region['all_diseases'].extend([getattr(mstat, 'disease') for mstat in region['marker_stats']])

                other_hits_query = ElasticQuery(
                        BoolQuery(must_arr=[RangeQuery("tier", lte=2), Query.terms("marker", region['markers'])],
                                  must_not_arr=[Query.terms("dil_study_id", study_ids)]))
                other_hits = Search(other_hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'),
                                    size=100).search()
                for h in other_hits.docs:
                        if h.disease is not None:
                            region['all_diseases'].append(h.disease)
                region['all_diseases'] = list(set(region['all_diseases']))

            # get markers
            if show_markers:
                query = ElasticQuery(Query.terms("id", all_markers), sources=['id', 'alt', 'ref', 'seqid', 'start'])
                marker_docs = Search(search_query=query, idx=ElasticSettings.idx('MARKER', 'MARKER'),
                                     size=len(all_markers)).search().docs
                for doc in Document.sorted_alphanum(marker_docs, 'seqid'):
                    marker_id = getattr(doc, 'id')
                    region_name = ''
                    for region in regions:
                        if marker_id in region['markers']:
                            region_name = region['region_name']
                            break
                    regions.append({
                        'marker_id': marker_id,
                        'seqid': 'chr'+getattr(doc, 'seqid'),
                        'rstart': getattr(doc, 'start'),
                        'ref': getattr(doc, 'ref'),
                        'alt': getattr(doc, 'alt'),
                        'region_name': region_name
                    })

            # get genes
            if show_genes:
                all_genes.extend(ens_all_cand_genes)
                gene_docs = GeneDocument.get_genes(all_genes, sources=['start', 'stop', 'chromosome',
                                                                       'symbol', 'biotype'])
                for doc in Document.sorted_alphanum(gene_docs, 'chromosome'):
                    ensembl_id = doc.doc_id()
                    region_name = ''
                    candidate_gene = 0
                    for region in regions:
                        if ('genes' in region and
                            (ensembl_id in region['genes']['region']['coding'] or
                             ensembl_id in region['genes']['region']['non_coding'] or
                             ensembl_id in region['ens_cand_genes'])):
                            region_name = region['region_name']
                            candidate_gene = 1 if ensembl_id in region['ens_cand_genes'] else 0
                            break
                    regions.append({
                        'ensembl_id': ensembl_id,
                        'seqid': 'chr'+getattr(doc, 'chromosome'),
                        'rstop': getattr(doc, 'start'),
                        'rstart': getattr(doc, 'stop'),
                        'symbol': getattr(doc, 'symbol'),
                        'biotype': getattr(doc, 'biotype'),
                        'region_name': region_name,
                        'candidate_gene': candidate_gene
                    })
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
