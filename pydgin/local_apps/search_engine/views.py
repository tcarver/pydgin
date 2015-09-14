''' Search engine views. '''
from django.shortcuts import render
from elastic.search import Search, ElasticQuery, Highlight, Suggest
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, Filter, BoolQuery
from django.http.response import JsonResponse


def suggester(request):
    ''' Auto suggester. '''
    query_dict = request.GET
    term = query_dict.get("term")

    idx_name = query_dict.get("idx")
    idx_dict = ElasticSettings.idx_props(idx_name)

    name = 'suggester'
    resp = Suggest.suggest(term, idx_dict['suggesters'], name=name, size=8)[name]
    return JsonResponse({"data": [opts['text'] for opts in resp[0]['options']]})


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''
    query_dict = request.GET
    if query_dict.get("query"):
        context = _search_engine(query_dict)
        return render(request, 'search_engine/result.html', context,
                      content_type='text/html')
    else:
        return render(request, 'search_engine/search.html', {},
                      content_type='text/html')


def _search_engine(query_dict):
    ''' Carry out a search and add results to the context object. '''
    query = query_dict.get("query")
    source_filter = ['symbol', 'synonyms', "dbxrefs.*", 'biotype', 'description',
                     'pathway_name', 'id', 'journal', 'rscurrent', 'name', 'code']
    search_fields = []

    # build search_fields from user input filter fields
    for it in query_dict.items():
        if len(it) == 2:
            if it[0] == 'query':
                continue
            parts = it[1].split(":")
            if len(parts) == 3:
                search_fields.append(parts[1]+"."+parts[2])
            elif len(parts) == 2:
                search_fields.append(parts[1])

    if len(search_fields) == 0:
        search_fields = list(source_filter)
        search_fields.extend(['abstract', 'title', 'authors.name', 'pmids', 'gene_sets'])
    source_filter.extend(['pmid', 'build_id', 'ref', 'alt'])

    idx_name = query_dict.get("idx")
    idx_dict = ElasticSettings.idx_props(idx_name)
    query_filters = _get_query_filters(query_dict)
    aggs = Aggs([Agg("biotypes", "terms", {"field": "biotype", "size": 0}),
                 Agg("categories", "terms", {"field": "_type", "size": 0})])
    highlight = Highlight(search_fields, pre_tags="<strong>", post_tags="</strong>", number_of_fragments=0)
    search = ElasticQuery.query_string(query, fields=search_fields, sources=source_filter,
                                       highlight=highlight, query_filter=query_filters)
    elastic = Search(search_query=search, aggs=aggs, search_from=0, size=50,
                     idx=idx_dict['idx'], idx_type=idx_dict['idx_type'])
    result = elastic.search()

    mappings = elastic.get_mapping()
    _update_mapping_filters(mappings, result.aggs)

    return {'data': result.docs, 'aggs': result.aggs,
            'query': query, 'idx_name': idx_name,
            'fields': search_fields, 'mappings': mappings,
            'hits_total': result.hits_total}


def _get_query_filters(q_dict):
    ''' Build query bool filter. If biotypes are specified add them to the filter and
    allow for other non-gene types.
    @type  q_dict: dict
    @param q_dict: request dictionary.
    '''
    if not q_dict.getlist("biotypes") and not q_dict.getlist("categories"):
        return None

    query_bool = BoolQuery()
    if q_dict.getlist("biotypes"):
        query_bool.should(Query.terms("biotype", q_dict.getlist("biotypes"), minimum_should_match=0))
        type_filter = [Query.query_type_for_filter(c) for c in q_dict.getlist("categories") if c != "gene"]
        if len(type_filter) > 0:
            query_bool.should(type_filter)

    if q_dict.getlist("categories"):
        query_bool.must(Query.terms("_type", q_dict.getlist("categories"), minimum_should_match=0))
    return Filter(query_bool)


def _update_mapping_filters(mappings, aggs):
    ''' Change the mapping dictionary for displaying as a search filter. Remove indices
    from the mapping that have no results (using the category/type aggregation.
    Also use the index key rather than name.

    @type  mappings: dict
    @param mappings: Elastic indices mappings.
    @type  aggs: L{Aggs}
    @param aggs: Search query aggregation.
    '''

    idx_types = [agg['key'] for agg in aggs['categories'].get_buckets()]
    idx_names = list(mappings.keys())
    idxs = ElasticSettings.attrs().get('IDX')
    for idx in idx_names:
        idx_key = _get_dict_key_by_value(idxs, idx)
        for t in mappings[idx]["mappings"].keys():
            if t in idx_types:
                mappings[idx_key] = mappings[idx]
                break

        # auto is a publication index type
        if 'auto' in mappings[idx]["mappings"]:
            mappings[idx]["mappings"]["publication"] = mappings[idx]["mappings"]["auto"]
            del mappings[idx]["mappings"]["auto"]

        del mappings[idx]


def _get_dict_key_by_value(mydict, val):
    ''' Get the key for the val in the dictionary.
    @type  mydict: dict
    @param mydict: The dictionary.
    @type  val: value
    @param val: A value in the dictionary.
    '''
    for k, v in mydict.items():
        if isinstance(v, str) and v == val:
            return k
        elif isinstance(v, dict) and v['name'] == val:
            return k
