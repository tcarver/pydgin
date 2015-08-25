from django.shortcuts import render
from django.http.response import JsonResponse
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def gene_page(request):
    ''' Renders a gene page. '''
    query_dict = request.GET
    gene = query_dict.get("g")
    query = ElasticQuery(Query.ids([gene]))
    elastic = Search(query, idx=ElasticSettings.idx('GENE'), size=5)
    res = elastic.search()
    if res.hits_total == 1:
        print(res.docs[0].__dict__)
        context = {'gene': res.docs[0]}
        return render(request, 'gene/gene.html', context,
                      content_type='text/html')


def pub_details(request):
    ''' Get PMID details. '''
    pmids = request.POST.getlist("pmids[]")
    query = ElasticQuery(Query.ids(pmids))
    elastic = Search(query, idx=ElasticSettings.idx('PUBLICATION'), size=len(pmids))
    return JsonResponse(elastic.get_json_response()['hits'])


def interaction_details(request):
    ''' Get interaction details for a given ensembl ID. '''
    ens_id = request.POST.get('ens_id')
    query = ElasticQuery.has_parent('gene', Query.ids(ens_id))
    elastic = Search(query, idx=ElasticSettings.idx('GENE'), size=100)
    return JsonResponse(elastic.get_json_response()['hits'])

