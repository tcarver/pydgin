''' Gene views. '''
from django.http.response import JsonResponse
from elastic.search import ElasticQuery, Search, ScanAndScroll
from elastic.query import Query, Filter
from elastic.elastic_settings import ElasticSettings
from django.http import Http404
from django.contrib import messages
from django.conf import settings
import collections
from gene.document import GeneDocument
from core.document import PublicationDocument
from core.views import SectionMixin, CDNMixin
from django.views.generic.base import TemplateView


class GeneView(CDNMixin, SectionMixin, TemplateView):
    ''' Renders a gene page. '''
    template_name = "gene/index.html"
    sections_name = "GeneView"

    def get_context_data(self, **kwargs):
        context = super(GeneView, self).get_context_data(**kwargs)
        return GeneView.get_gene(self.request, kwargs['gene'], context)

    @classmethod
    def get_gene(cls, request, gene, context):
        if gene is None:
            messages.error(request, 'No gene name given.')
            raise Http404()
        res = Search(search_query=ElasticQuery(Query.ids(gene.split(','))),
                     idx=ElasticSettings.idx('GENE', 'GENE'), size=9).search()
        if res.hits_total == 0:
            messages.error(request, 'Gene(s) '+gene+' not found.')
        elif res.hits_total < 9:
            context['features'] = res.docs
            context['title'] = ', '.join([getattr(doc, 'symbol') for doc in res.docs])
            return context


def pub_details(request):
    ''' Get PMID details. '''
    pmids = request.POST.getlist("pmids[]")
    query = ElasticQuery(Query.ids(pmids))
    elastic = Search(query, idx=ElasticSettings.idx('PUBLICATION', 'PUBLICATION'), size=len(pmids))
    return JsonResponse(elastic.get_json_response()['hits'])


def interaction_details(request):
    ''' Get interaction details for a given ensembl ID. '''
    ens_id = request.POST.get('ens_id')
    query = ElasticQuery.has_parent('gene', Query.ids(ens_id))
    elastic = Search(query, idx=ElasticSettings.idx('GENE', 'INTERACTIONS'), size=500)

    interaction_hits = elastic.get_json_response()['hits']
    ens_ids = []
    for hit in interaction_hits['hits']:
        for interactor in hit['_source']['interactors']:
            ens_ids.append(interactor['interactor'])
    docs = _get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])
    for hit in interaction_hits['hits']:
        for interactor in hit['_source']['interactors']:
            iid = interactor['interactor']
            try:
                interactor['symbol'] = getattr(docs[iid], 'symbol')
            except KeyError:
                interactor['symbol'] = iid

    return JsonResponse(interaction_hits)


def genesets_details(request):
    ''' Get pathway gene sets for a given ensembl ID. '''
    ens_id = request.POST.get('ens_id')
    geneset_filter = Filter(Query.query_string(ens_id, fields=["gene_sets"]).query_wrap())
    query = ElasticQuery.filtered(Query.match_all(), geneset_filter)
    elastic = Search(query, idx=ElasticSettings.idx('GENE', 'PATHWAY'), size=500)
    genesets_hits = elastic.get_json_response()['hits']
    ens_ids = []
    for hit in genesets_hits['hits']:
        for ens_id in hit['_source']['gene_sets']:
            ens_ids.append(ens_id)
    docs = _get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])

    for hit in genesets_hits['hits']:
        genesets = {}
        for ens_id in hit['_source']['gene_sets']:
            try:
                genesets[ens_id] = getattr(docs[ens_id], 'symbol')
            except KeyError:
                genesets[ens_id] = ens_id
        hit['_source']['gene_sets'] = genesets
    return JsonResponse(genesets_hits)


def studies_details(request):
    ''' Get studies for a given ensembl ID. '''
    ens_id = request.POST.get('ens_id')
    sfilter = Filter(Query.query_string(ens_id, fields=["genes"]).query_wrap())
    query = ElasticQuery.filtered(Query.match_all(), sfilter)
    elastic = Search(query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'), size=500)
    study_hits = elastic.get_json_response()['hits']

    ens_ids = []
    pmids = []
    for hit in study_hits['hits']:
        if 'pmid' in hit['_source']:
            pmids.append(hit['_source']['pmid'])
        for ens_id in hit['_source']['genes']:
            ens_ids.append(ens_id)
    docs = _get_gene_docs_by_ensembl_id(ens_ids, ['symbol'])
    pub_docs = _get_pub_docs_by_pmid(pmids, sources=['authors.name', 'journal'])

    for hit in study_hits['hits']:
        genes = {}
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
                     'author': authors[0]['name'].rsplit(None, 1)[-1],
                     'journal': journal}
            except KeyError:
                hit['_source']['pmid'] = {'pmid': pmid}

    return JsonResponse(study_hits)


def _get_gene_docs_by_ensembl_id(ens_ids, sources=None):
    ''' Get the gene symbols for the corresponding array of ensembl IDs.
    A dictionary is returned with the key being the ensembl ID and the
    value the gene document. '''
    genes = {}

    def get_genes(resp_json):
        hits = resp_json['hits']['hits']
        for hit in hits:
            genes[hit['_id']] = GeneDocument(hit)
    query = ElasticQuery(Query.ids(ens_ids), sources=sources)
    ScanAndScroll.scan_and_scroll(ElasticSettings.idx('GENE'), call_fun=get_genes, query=query)
    return genes


def _get_pub_docs_by_pmid(pmids, sources=None):
    ''' Get the gene symbols for the corresponding array of ensembl IDs.
    A dictionary is returned with the key being the ensembl ID and the
    value the gene document. '''
    pubs = {}

    def get_pubs(resp_json):
        hits = resp_json['hits']['hits']
        for hit in hits:
            pubs[hit['_id']] = PublicationDocument(hit)
    query = ElasticQuery(Query.ids(pmids), sources=sources)
    ScanAndScroll.scan_and_scroll(ElasticSettings.idx('PUBLICATION'), call_fun=get_pubs, query=query)
    return pubs


class GeneViewParams(GeneView):
    ''' Renders a gene page. '''
    def get_context_data(self, **kwargs):
        return super(GeneViewParams, self).get_context_data(gene=self.request.GET.get('g'), **kwargs)


class JSTestView(CDNMixin, TemplateView):
    ''' Renders a marker page. '''
    template_name = "js_test/test.html"

    def get_context_data(self, **kwargs):
        context = super(JSTestView, self).get_context_data(**kwargs)
        if not (settings.DEBUG or settings.TESTMODE):
            raise Http404()
        return context
