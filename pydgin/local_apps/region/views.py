''' Region views. '''
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.search import ElasticQuery, Search

from core.views import CDNMixin, SectionMixin
from region.utils import Region


class RegionView(CDNMixin, SectionMixin, TemplateView):
    ''' Renders a region page. '''
    template_name = "region/index.html"

    def get_context_data(self, **kwargs):
        context = super(RegionView, self).get_context_data(**kwargs)
        return RegionView.get_region(self.request, kwargs['region'], context)

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
            names = ', '.join([getattr(doc, 'region_name') for doc in res.docs])
            REGIONS = [Region.pad_region_doc(doc) for doc in res.docs]
            context['features'] = REGIONS
            context['title'] = names
            return context
        raise Http404()


class RegionViewParams(RegionView):
    ''' Renders a region page. '''
    def get_context_data(self, **kwargs):
        return super(RegionViewParams, self).get_context_data(region=self.request.GET.get('r'), **kwargs)
