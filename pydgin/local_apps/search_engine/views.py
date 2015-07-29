from django.shortcuts import render
from elastic.search import Search, ElasticQuery, Highlight, Suggest
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from elastic.query import AndFilter, Query, Filter
from django.http.response import JsonResponse


def suggester(request):
    ''' Auto completion suggester. '''
    query_dict = request.GET
    term = query_dict.get("term")

    elastic_attrs = ElasticSettings.attrs()
    suggesters = elastic_attrs.get('SEARCH').get('AUTOCOMPLETE-SUGGESTER')
    idx = ','.join(elastic_attrs.get('IDX')[idx_name] for idx_name in suggesters)

    name = 'suggester'
    resp = Suggest.suggest(term, idx, name=name, size=8)[name]
    data = []
    for opts in resp[0]['options']:
        data.append(opts['text'])
    return JsonResponse({"data": data})


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''
    context = {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}
    query_dict = request.GET
    if query_dict.get("query"):
        query = query_dict.get("query")
        source_filter = ['symbol', 'synonyms', "dbxrefs.ensembl", 'biotype', 'description',
                         'pathway_name', 'id', 'journal', 'rscurrent',
                         'name', 'code']
        search_fields = []

        for it in query_dict.items():
            if len(it) == 2:
                if it[0] == 'query':
                    continue
                parts = it[1].split(":")
                if len(parts) == 3:
                    search_fields.append(parts[1]+"."+parts[2])
                elif len(parts) == 2:
                    search_fields.append(parts[1])

        if len(search_fields) == 0 and not (isinstance(query, int) or query.isdigit()):
            search_fields = list(source_filter)
            search_fields.extend(['abstract', 'title', 'authors.name', 'pmids', 'gene_sets'])
        source_filter.extend(['pmid', 'build_id'])

        idx_name = query_dict.get("idx")
        idx_dict = _idx_search(idx_name, query_dict)
        query_filters = _get_filters(query_dict)
        aggs = Aggs([Agg("biotypes", "terms", {"field": "biotype", "size": 0}),
                     Agg("categories", "terms", {"field": "_type", "size": 0})])
        highlight = Highlight(search_fields, pre_tags="<strong>", post_tags="</strong>", number_of_fragments=0)
        search = ElasticQuery.query_string(query, fields=search_fields, sources=source_filter,
                                           highlight=highlight, query_filter=query_filters)
        elastic = Search(search_query=search, aggs=aggs, search_from=0, size=50,
                         idx=idx_dict['idx'], idx_type=idx_dict['idx_type'])
        result = elastic.search()
        mappings = elastic.get_mapping()
        context.update({'data': result.docs, 'aggs': result.aggs,
                        'query': query, 'idx_name': idx_name,
                        'fields': search_fields, 'mappings': mappings,
                        'hits_total': result.hits_total})
        return render(request, 'search_engine/result.html', context,
                      content_type='text/html')
    else:
        return render(request, 'search_engine/search.html', context,
                      content_type='text/html')


def _idx_search(idx_name, query_dict):
    ''' Build the search index names and types and return as a dictionary. '''
    elastic_attrs = ElasticSettings.attrs()
    search_idx = elastic_attrs.get('SEARCH').get('IDX_TYPES')
    if idx_name == 'ALL':
        return {
            "idx": ','.join(elastic_attrs.get('IDX')[idx_name] for idx_name in search_idx.keys()),
            "idx_type": ','.join(itype for types in search_idx.values() for itype in types)
        }
    else:
        return {
            "idx": elastic_attrs.get('IDX')[idx_name],
            "idx_type": ','.join(it for it in search_idx[idx_name])
        }


def _get_filters(query_dict):
    ''' Build query filters. '''
    query_arr = []
    if query_dict.getlist("biotypes"):
        query_arr.append(Query.terms("biotype", query_dict.getlist("biotypes"), minimum_should_match=0))

    if query_dict.getlist("categories"):
        query_arr.append(Query.terms("_type", query_dict.getlist("categories"), minimum_should_match=0))

    if len(query_arr) == 1:
        return Filter(query_arr[0])
    elif len(query_arr) > 1:
        return AndFilter(query_arr)
    return None
