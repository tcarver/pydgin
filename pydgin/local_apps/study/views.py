''' Study views. '''
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView, View

from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, Filter
from elastic.search import ElasticQuery, Search
from study.document import StudyDocument
from django.http.response import JsonResponse
from gene import utils


class StudyView(TemplateView):
    ''' Renders a study page. '''
    template_name = "study/index.html"

    def get_context_data(self, **kwargs):
        context = super(StudyView, self).get_context_data(**kwargs)
        study = kwargs['study'] if 'study' in kwargs else self.request.GET.get('s')
        return StudyView.get_study(self.request, study, context)

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


class StudySectionView(View):
    ''' Study section for gene/marker/region. '''

    def post(self, request, *args, **kwargs):
        ens_id = self.request.POST.get('ens_id')
        marker = self.request.POST.get('marker')
        markers = self.request.POST.getlist('markers[]')

        if ens_id:
            sfilter = Filter(Query.query_string(ens_id, fields=["genes"]).query_wrap())
        elif marker:
            sfilter = Filter(Query.query_string(marker, fields=["marker"]).query_wrap())
        elif markers:
            sfilter = Filter(Query.query_string(' '.join(markers), fields=["marker"]).query_wrap())

        query = ElasticQuery.filtered(Query.match_all(), sfilter)
        elastic = Search(query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'), size=500)
        study_hits = elastic.get_json_response()['hits']

        ens_ids = []
        pmids = []
        for hit in study_hits['hits']:
            if 'pmid' in hit['_source']:
                pmids.append(hit['_source']['pmid'])
            if 'genes' in hit['_source']:
                for ens_id in hit['_source']['genes']:
                    ens_ids.append(ens_id)
        docs = utils.get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])
        pub_docs = utils.get_pub_docs_by_pmid(pmids, sources=['authors.name', 'journal'])

        for hit in study_hits['hits']:
            genes = {}
            if 'genes' in hit['_source']:
                for ens_id in hit['_source']['genes']:
                    try:
                        genes[ens_id] = getattr(docs[ens_id], 'symbol')
                    except KeyError:
                        genes = {ens_id: ens_id}
            hit['_source']['genes'] = genes
            if 'pmid' in hit['_source']:
                pmid = hit['_source']['pmid']
                try:
                    authors = getattr(pub_docs[pmid], 'authors')
                    journal = getattr(pub_docs[pmid], 'journal')
                    hit['_source']['pmid'] = \
                        {'pmid': pmid,
                         'author': authors[0]['name'].rsplit(None, 1)[-1] if authors else "",
                         'journal': journal}
                except KeyError:
                    hit['_source']['pmid'] = {'pmid': pmid}

        return JsonResponse(study_hits)
