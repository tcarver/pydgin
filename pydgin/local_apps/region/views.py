''' Region views. '''

import locale
import re

from criteria.helper.region_criteria import RegionCriteria
from django.contrib import messages
from django.http import Http404
from django.http.response import JsonResponse
from django.views.generic.base import TemplateView
from elastic.aggs import Aggs, Agg
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, Filter, BoolQuery, RangeQuery
from elastic.search import ElasticQuery, Search, Sort

from core.views import SectionMixin
from pydgin import pydgin_settings
from region.utils import Region


class RegionView(SectionMixin, TemplateView):
    ''' Renders a region page. '''
    template_name = "region/index.html"

    def get_context_data(self, **kwargs):
        context = super(RegionView, self).get_context_data(**kwargs)
        region = kwargs['region'] if 'region' in kwargs else self.request.GET.get('r')
        if region is None:
            messages.error(self.request, 'No region given.')
            raise Http404()

        if re.search("[p|q]\d+", region.lower()) is None:
            regionDocs = Region.loci_to_regions([region.lower()])
            if len(regionDocs) == 0:
                messages.error(self.request, 'No region found.')
                raise Http404()

            region = regionDocs[0].doc_id()
        return RegionView.get_region(self.request, region, context)

    @classmethod
    def get_region(cls, request, region, context):
        if region is None:
            messages.error(request, 'No region given.')
            raise Http404()
        query = ElasticQuery(Query.ids(region.split(',')))
        elastic = Search(query, idx=ElasticSettings.idx('REGION', 'REGION'), size=5)
        res = elastic.search()
        if res.hits_total == 0:
            messages.error(request, 'Region(s) '+region+' not found.')
        elif res.hits_total < 9:
            context['features'] = [Region.pad_region_doc(doc) for doc in res.docs]
            context['title'] = ', '.join([getattr(doc, 'region_name') for doc in res.docs])
            return context
        raise Http404()


def criteria_details(request):
    ''' Get criteria details for a given region ID. '''
    feature_id = request.POST.get('feature_id')
    criteria_details = RegionCriteria.get_criteria_details(feature_id)
    return JsonResponse(criteria_details)


class RegionTableView(TemplateView):
    '''Renders a table of all regions for a specific disease'''
    template_name = 'region/region_table.html'

    def get_context_data(self, **kwargs):
        context = super(RegionTableView, self).get_context_data(**kwargs)
        disease = kwargs['disease'] if 'disease' in kwargs else self.request.GET.get('d')
        return RegionTableView.get_regions(self.request, disease, context)

    @classmethod
    def get_regions(cls, request, dis, context):
        is_authenticated = False
        build = pydgin_settings.DEFAULT_BUILD

        locus_start = Agg('region_start', 'min', {'field': 'build_info.start'})
        locus_end = Agg('region_end', 'max', {'field': 'build_info.end'})
        match_agg = Agg('filtered_result', 'filter', Query.match("build_info.build", build).query_wrap(),
                        sub_agg=[locus_start, locus_end])
        build_info_agg = Agg('build_info', 'nested', {"path": 'build_info'}, sub_agg=[match_agg])

        query = ElasticQuery(Query.terms("code", [dis.lower().split(',')]))
        elastic = Search(query, idx=ElasticSettings.idx('DISEASE', 'DISEASE'), size=5)
        res = elastic.search()
        if res.hits_total == 0:
            messages.error(request, 'Disease '+dis+' not found.')
            raise Http404()

        disease = res.docs[0]
        context['title'] = getattr(disease, "name")+" Regions"

        query = ElasticQuery(Query.term("disease", dis.lower()))
        elastic = Search(query, idx=ElasticSettings.idx('REGION', 'DISEASE_LOCUS'),
                         qsort=Sort('seqid:asc,locus_id:asc'), size=200)
        res = elastic.search()
        if res.hits_total == 0:
            messages.error(request, 'No regions found for '+dis+'.')
            raise Http404()

        regions = []
        for r in res.docs:
            region = {
                'region_name': getattr(r, "region_name"),
                'locus_id': getattr(r, "locus_id"),
                'seqid': 'chr'+getattr(r, "seqid")
            }
            hits = getattr(r, "hits")
            # hits_query = ElasticQuery(Query.ids(hits))
            hits_query = ElasticQuery.filtered(Query.ids(hits),
                                               Filter(BoolQuery(should_arr=[Query.missing_terms("field", "group_name")]
                                                                 )))
            hits_res = Search(hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'),
                              aggs=Aggs(build_info_agg), size=len(hits)).search()
            if hits_res.hits_total > 0:
                build_info = getattr(hits_res.aggs['build_info'], 'filtered_result')
                region['start'] = str(locale.format("%d",  int(build_info['region_start']['value']), grouping=True))
                region['end'] = str(locale.format("%d",  int(build_info['region_end']['value']), grouping=True))
                region['hits'] = hits_res.docs
                region['markers'] = [h.marker for h in hits_res.docs]

                stats_query = ElasticQuery.filtered(Query.terms("marker", region['markers']),
                                                    Filter(RangeQuery("p_value", lte=5E-08)))
                stats_result = Search(stats_query, idx=ElasticSettings.idx("IC_STATS")).search()
                '''@TODO add authentication here.'''
                region['marker_stats'] = stats_result.docs

                (region_coding, region_non_coding) = get_genes_for_region(getattr(r, "seqid"),
                                                                          int(build_info['region_start']['value']),
                                                                          int(build_info['region_end']['value']))
                (coding_down, non_coding_down) = get_genes_for_region(getattr(r, "seqid"),
                                                                      int(build_info['region_start']['value'])-500000,
                                                                      int(build_info['region_start']['value']))
                (coding_up, non_coding_up) = get_genes_for_region(getattr(r, "seqid"),
                                                                  int(build_info['region_end']['value']),
                                                                  int(build_info['region_end']['value'])+500000)
                genes = {
                    'upstream': {'coding': coding_up, 'non_coding': non_coding_up},
                    'region': {'coding': region_coding, 'non_coding': region_non_coding},
                    'downstream': {'coding': coding_down, 'non_coding': non_coding_down},
                }
                region['genes'] = genes
                regions.append(region)
        context['regions'] = regions
        context['disease_code'] = dis.lower(),
        return context


def get_genes_for_region(seqid, start, end, must=None):
    coding = []
    non_coding = []
    gene_index = ElasticSettings.idx('GENE', idx_type='GENE')
    elastic = Search.range_overlap_query(seqid=seqid.lower(), start_range=start, end_range=end,
                                         idx=gene_index, field_list=['start', 'stop', '_id', 'biotype', 'symbol'],
                                         seqid_param="chromosome", end_param="stop", size=10000)
    for doc in elastic.search().docs:
        if getattr(doc, "biotype") == "protein_coding":
            coding.append(doc)
        else:
            non_coding.append(doc)
    return (coding, non_coding)
