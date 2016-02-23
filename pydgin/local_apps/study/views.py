''' Study views. '''
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView

from core.views import CDNMixin
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.search import ElasticQuery, Search
from study.document import StudyDocument


class StudyView(CDNMixin, TemplateView):
    ''' Renders a study page. '''
    template_name = "study/index.html"

    def get_context_data(self, **kwargs):
        context = super(StudyView, self).get_context_data(**kwargs)
        return StudyView.get_study(self.request, kwargs['study'], context)

    @classmethod
    def get_study(cls, request, study, context):
        if study is None:
            messages.error(request, 'No study id given.')
            raise Http404()
        query = ElasticQuery(Query.ids(study.split(',')))
        elastic = Search(query, idx=ElasticSettings.idx('STUDY', 'STUDY'), size=5)
        res = elastic.search(obj_document=StudyDocument)
        if res.hits_total == 0:
            messages.error(request, 'Study(s) '+study+' not found.')
        elif res.hits_total < 9:
            names = ', '.join([getattr(doc, 'study_name') for doc in res.docs])
            context['features'] = res.docs
            context['title'] = names
            return context
        raise Http404()


class StudyViewParams(StudyView):
    ''' Renders a study page. '''
    def get_context_data(self, **kwargs):
        return super(StudyViewParams, self).get_context_data(study=self.request.GET.get('s'), **kwargs)
