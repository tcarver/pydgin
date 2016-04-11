''' Region views. '''

import json
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
import gene
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
        # is_authenticated = False
        build = pydgin_settings.DEFAULT_BUILD
        elastic_url = ElasticSettings.url()

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
            hits_query = ElasticQuery.filtered(
                            Query.ids(hits),
                            Filter(BoolQuery(should_arr=[Query.missing_terms("field", "group_name")])))
            hits_res = Search(hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'),
                              aggs=Aggs(build_info_agg), size=len(hits)).search()
            if hits_res.hits_total > 0:
                diseases = [dis]
                build_info = getattr(hits_res.aggs['build_info'], 'filtered_result')
                regions_start = int(build_info['region_start']['value'])
                regions_stop = int(build_info['region_end']['value'])

                region['start'] = str(locale.format("%d",  regions_start, grouping=True))
                region['end'] = str(locale.format("%d",  regions_stop, grouping=True))

                r_docs = hits_res.docs
                region['hits'] = _process_hits(r_docs, diseases)
                region['markers'] = list(set([h.marker for h in r_docs]))
                cand_genes = {}
                for h in r_docs:
                    if h.genes is not None:
                        cand_genes.update(gene.utils.get_gene_docs_by_ensembl_id(h.genes))
                region['cand_genes'] = cand_genes

                stats_query = ElasticQuery.filtered(Query.terms("marker", region['markers']),
                                                    Filter(RangeQuery("p_value", lte=5E-08)))
                stats_result = Search(stats_query, idx=ElasticSettings.idx("IC_STATS")).search()

                study_ids = []
                for doc in stats_result.docs:
                    idx = doc.index()
                    idx_type = doc.type()
                    meta_response = Search.elastic_request(elastic_url, idx + '/' + idx_type + '/_mapping',
                                                           is_post=False)
                    elastic_meta = json.loads(meta_response.content.decode("utf-8"))
                    meta_info = elastic_meta[idx]['mappings'][idx_type]['_meta']
                    setattr(doc, "disease", meta_info['disease'])
                    if re.match(r"^gdx", meta_info['study'].lower()):
                        setattr(doc, "dil_study_id", meta_info['study'])
                        study_ids.append(meta_info['study'])
                    setattr(h, "p_value", float(getattr(h, "p_value")))
                study_ids = list(set(study_ids))

                '''@TODO add authentication here.'''
                region['marker_stats'] = stats_result.docs

                other_hits_query = ElasticQuery(
                        BoolQuery(must_arr=[RangeQuery("tier", lte=2), Query.terms("marker", region['markers'])],
                                  must_not_arr=[Query.terms("dil_study_id", study_ids)]))
                other_hits = Search(other_hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'),
                                    size=100).search()

                region['extra_markers'] = _process_hits(other_hits.docs, diseases)

                (all_coding, all_non_coding) = get_genes_for_region(getattr(r, "seqid"),
                                                                    regions_start-500000, regions_stop+500000)
                (region_coding, coding_up, coding_down) = _region_up_down(all_coding, regions_start, regions_stop)
                (region_non_coding, non_coding_up, non_coding_down) = \
                    _region_up_down(all_non_coding, regions_start, regions_stop)
                genes = {
                    'upstream': {'coding': coding_up, 'non_coding': non_coding_up},
                    'region': {'coding': region_coding, 'non_coding': region_non_coding},
                    'downstream': {'coding': coding_down, 'non_coding': non_coding_down},
                }
                region['genes'] = genes
                region['all_diseases'] = list(set(diseases))
                regions.append(region)
                #break

        context['regions'] = regions
        context['disease_code'] = [dis]
        context['disease'] = getattr(disease, "name")
        return context


def _process_hits(docs, diseases):
    ''' Process docs to add disease, P-values, odds ratios. '''
    for h in docs:
        if h.disease is not None:
            diseases.append(h.disease)

        setattr(h, "p_value", None)
        if getattr(h, "p_values")['combined'] is not None:
            setattr(h, "p_value", float(getattr(h, "p_values")['combined']))
            setattr(h, "p_val_src", "C")
        elif getattr(h, "p_values")['discovery'] is not None:
            setattr(h, "p_value", float(getattr(h, "p_values")['discovery']))
            setattr(h, "p_val_src", "D")

        setattr(h, "odds_ratio", None)
        setattr(h, "or_bounds", None)
        setattr(h, "risk_allele", None)
        if getattr(h, "odds_ratios")['combined']['or'] != None:
            setattr(h, "odds_ratio", getattr(h, "odds_ratios")['combined']['or'])
            setattr(h, "or_src", "C")
            or_combined = getattr(h, "odds_ratios")['combined']
            if or_combined['upper'] != None:
                if float(or_combined['or']) > 1:
                    setattr(h, "or_bounds", "("+or_combined['lower']+"-"+or_combined['upper']+")")
                else:
                    setattr(h, "or_bounds", "("+str(float("{0:.2f}".format(1/float(or_combined['upper'])))) + "-" +
                            str(float("{0:.2f}".format(1/float(or_combined['lower']))))+")")

        or_discovery = getattr(h, "odds_ratios")['discovery']
        if or_discovery['or'] != None:
            setattr(h, "odds_ratio", or_discovery['or'])
            setattr(h, "or_src", "D")
            if or_discovery['upper'] != None:
                if float(or_discovery['or']) > 1:
                    setattr(h, "or_bounds", "("+or_discovery['lower']+"-"+or_discovery['upper']+")")
                else:
                    setattr(h, "or_bounds", "("+str(float("{0:.2f}".format(1/float(or_discovery['upper'])))) + "-" +
                            str(float("{0:.2f}".format(1/float(or_discovery['lower']))))+")")

        if getattr(h, "odds_ratio") is not None:
            if float(getattr(h, "odds_ratio")) > 1:
                setattr(h, "risk_allele", getattr(h, "alleles")['minor'])
            else:
                setattr(h, "odds_ratio", str(float("{0:.2f}".format(1/float(getattr(h, "odds_ratio"))))))
                setattr(h, "risk_allele", getattr(h, "alleles")['major'])
    return docs


def _region_up_down(genes, regions_start, regions_stop):
    ''' Separate into within region and upstream and downstream arrays.'''
    region = []
    up = []
    down = []
    for doc in genes:
        this_start = getattr(doc, "start")
        this_stop = getattr(doc, "stop")
        if((this_start > regions_start and this_start < regions_stop) or
           (this_stop > regions_start and this_stop < regions_stop) or
           (this_start < regions_start and this_stop > regions_stop)):
            region.append(doc)
        elif this_start < regions_start:
            down.append(doc)
        else:
            up.append(doc)
    return (region, up, down)


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
