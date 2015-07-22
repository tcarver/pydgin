from django.shortcuts import render
from elastic.search import Search, ElasticQuery, Highlight
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''

    queryDict = request.GET
    if queryDict.get("query"):
        query = queryDict.get("query")
        source_filter = ['symbol', 'synonyms', "dbxrefs.ensembl", 'interaction_source', 'pathway_name', 'id', 'journal']
        highlight_fields = list(source_filter)
        highlight_fields.extend(['abstract', 'title', 'authors.LastName', 'authors.ForeName', 'pmids'])
        fields = []
        if not (isinstance(query, int) or query.isdigit()):
            fields.extend(highlight_fields)
        source_filter.extend(['PMID'])

        idx_name = queryDict.get("idx")
        idx_type = ''
        if idx_name == 'ALL':
            idx = ElasticSettings.indices_str()
        else:
            idx = ElasticSettings.attrs().get('IDX')[idx_name]
            idx_type = ','.join(it for it in ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES')[idx_name])

        aggs = Aggs(Agg("categories", "terms", {"field": "_type", "size": 0}))
        highlight = Highlight(highlight_fields, pre_tags="<strong>", post_tags="</strong>")
        search_query = ElasticQuery.query_string(query, fields=fields, sources=source_filter, highlight=highlight)
        elastic = Search(search_query=search_query, aggs=aggs, search_from=0, size=50,
                         idx=idx, idx_type=idx_type)
        result = elastic.search()
        mappings = elastic.get_mapping()
        context = {'data': result.docs,
                   'query': query,
                   'fields': fields,
                   'mappings': mappings[idx],
                   'hits_total': result.hits_total}

        return render(request, 'search_engine/result.html', context,
                      content_type='text/html')
    else:
        context = {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}
        return render(request, 'search_engine/search.html', context,
                      content_type='text/html')
