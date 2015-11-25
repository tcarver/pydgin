from django.shortcuts import render
from django.http.response import JsonResponse
from elastic.search import ElasticQuery, Search
from elastic.query import Query, Filter
from elastic.elastic_settings import ElasticSettings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from django.contrib import messages
from django.conf import settings
import collections


@ensure_csrf_cookie
def gene_page(request):
    ''' Renders a gene page. '''
    query_dict = request.GET
    gene = query_dict.get("g")
    if gene is None:
        messages.error(request, 'No gene name given.')
        raise Http404()
    query = ElasticQuery(Query.ids(gene.split(',')))
    elastic = Search(query, idx=ElasticSettings.idx('GENE', 'GENE'), size=5)
    res = elastic.search()
    if res.hits_total == 0:
        messages.error(request, 'Gene(s) '+gene+' not found.')
    elif res.hits_total < 9:
        symbols = ', '.join([getattr(doc, 'symbol') for doc in res.docs])
        context = {'genes': res.docs, 'title': symbols, 'criteria': _get_gene_criteria(res.docs, 'gene', 'symbol', 'GENE')}
        return render(request, 'gene/gene.html', context,
                      content_type='text/html')
    raise Http404()


def _get_gene_criteria(docs, doc_type, doc_attr, idx_type_key):
    ''' Return a dictionary of gene name:criteria. '''
    genes = [getattr(doc, doc_attr).lower() for doc in docs if doc.type() == doc_type]
    query = Query.terms('Name', genes)
    sources = {"exclude": ['Primary id', 'Object class', 'Total score']}
    res = Search(ElasticQuery(query, sources=sources), idx=ElasticSettings.idx('CRITERIA', idx_type_key),
                 size=len(genes)).search()
    criteria = {}

    for doc in res.docs:
        od = collections.OrderedDict(sorted(doc.__dict__.items(), key=lambda t: t[0]))
        gene_name = getattr(doc, 'Name')
        criteria[gene_name] = [{attr.replace('_Hs', ''): value.split(':')} for attr, value in od.items()
                               if attr != 'Name' and attr != '_meta' and attr != 'OD_Hs' and not
                               value.startswith('0')]
        if hasattr(doc, 'OD_Hs') and not getattr(doc, 'OD_Hs').startswith('0'):
            if gene_name not in criteria:
                criteria[gene_name] = []
            criteria[gene_name].append({'OD': getattr(doc, 'OD_Hs').split(':')})

    return criteria


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
    elastic = Search(query, idx=ElasticSettings.idx('REGIONS', 'STUDIES'), size=500)
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
    query = ElasticQuery(Query.ids(ens_ids), sources=sources)
    elastic = Search(query, idx=ElasticSettings.idx('GENE'), size=len(ens_ids))
    return {doc.doc_id(): doc for doc in elastic.search().docs}


def _get_pub_docs_by_pmid(pmids, sources=None):
    ''' Get the gene symbols for the corresponding array of ensembl IDs.
    A dictionary is returned with the key being the ensembl ID and the
    value the gene document. '''
    query = ElasticQuery(Query.ids(pmids), sources=sources)
    elastic = Search(query, idx=ElasticSettings.idx('PUBLICATION'), size=len(pmids))
    return {doc.doc_id(): doc for doc in elastic.search().docs}


@ensure_csrf_cookie
def js_test(request):
    ''' Renders a gene page. '''
    if not (settings.DEBUG or settings.TESTMODE):
        raise Http404()
    return render(request, 'js_test/test.html', {}, content_type='text/html')
