''' Region views. '''

from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.search import ElasticQuery, Search, Sort

from core.views import SectionMixin
from region.utils import Region


class RegionView(SectionMixin, TemplateView):
    ''' Renders a region page. '''
    template_name = "region/index.html"

    def get_context_data(self, **kwargs):
        context = super(RegionView, self).get_context_data(**kwargs)
        region = kwargs['region'] if 'region' in kwargs else self.request.GET.get('r')
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


class RegionTableView(TemplateView):
    '''Renders a table of all regions for a specific disease'''
    template_name = 'region/region_table.html'

    def get_context_data(self, **kwargs):
        context = super(RegionTableView, self).get_context_data(**kwargs)
        disease = kwargs['disease'] if 'disease' in kwargs else self.request.GET.get('d')
        return RegionTableView.get_regions(self.request, disease, context)

    @classmethod
    def get_regions(cls, request, dis, context):
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
                'locus_id': getattr(r, "locus_id")
            }
            hits = getattr(r, "hits")
            hits_query = ElasticQuery(Query.ids(hits))
            hits_res = Search(hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'), size=len(hits)).search()
            region['hits'] = hits_res.docs
            regions.append(region)
        context['regions'] = regions
        context['disease_code'] = dis.lower(),
        return context























