''' Disease views. '''
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView

from core.views import CDNMixin
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.search import ElasticQuery, Search
from study.document import StudyDocument


class DiseaseView(CDNMixin, TemplateView):
    ''' Renders a disease page. '''
    template_name = "disease/index.html"

    def get_context_data(self, **kwargs):
        context = super(DiseaseView, self).get_context_data(**kwargs)
        return DiseaseView.get_disease(self.request, kwargs['disease'], context)

    @classmethod
    def get_disease(cls, request, disease, context):
        disease = disease.lower()
        if disease is None:
            messages.error(request, 'No disease given.')
            raise Http404()
        query = ElasticQuery(Query.terms("code", [disease.split(',')]))
        elastic = Search(query, idx=ElasticSettings.idx('DISEASE', 'DISEASE'), size=5)
        res = elastic.search()
        if res.hits_total == 0:
            messages.error(request, 'Disease(s) '+disease+' not found.')
        elif res.hits_total < 9:
            names = ', '.join([getattr(doc, 'name') for doc in res.docs])
            context['features'] = res.docs
            context['title'] = names
            return context
        raise Http404()


class DiseaseViewParams(DiseaseView):
    ''' Renders a study page. '''
    def get_context_data(self, **kwargs):
        return super(DiseaseViewParams, self).get_context_data(disease=self.request.GET.get('d'), **kwargs)
