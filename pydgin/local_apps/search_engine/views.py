from django.shortcuts import render
from elastic.search import Search, ElasticQuery, Highlight
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''

    queryDict = request.GET
    if queryDict.get("query"):
        query = queryDict.get("query")
        source_filter = ['symbol', 'synonyms', "dbxrefs.ensembl", 'pathway_name', 'id', 'journal', 'rscurrent']
        highlight_fields = list(source_filter)
        highlight_fields.extend(['abstract', 'title', 'authors.LastName', 'authors.ForeName', 'pmids', 'gene_sets'])
        search_fields = []

        for it in queryDict.items():
            if len(it) == 2:
                parts = it[1].split(":")
                if len(parts) > 1:
                    if len(parts) == 3:
                        search_fields.append(parts[1]+"."+parts[2])
                    elif len(parts) == 2:
                        search_fields.append(parts[1])

        if len(search_fields) == 0 and not (isinstance(query, int) or query.isdigit()):
            search_fields = list(source_filter)
            search_fields.extend(['abstract', 'title', 'authors.LastName', 'authors.ForeName', 'pmids', 'gene_sets'])

        highlight_fields = list(search_fields)

        source_filter.extend(['PMID'])

        idx_name = queryDict.get("idx")
        idx_type = ''
        if idx_name == 'ALL':
            idx_names = ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()
            type_arrs = ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').values()

            idx = ','.join(ElasticSettings.attrs().get('IDX')[idx_name] for idx_name in idx_names)
            idx_type = ','.join(itype for types in type_arrs for itype in types)
        else:
            idx = ElasticSettings.attrs().get('IDX')[idx_name]
            idx_type = ','.join(it for it in ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES')[idx_name])

        aggs = Aggs(Agg("categories", "terms", {"field": "_type", "size": 0}))
        highlight = Highlight(highlight_fields, pre_tags="<strong>", post_tags="</strong>", number_of_fragments=0)
        search_query = ElasticQuery.query_string(query, fields=search_fields,
                                                 sources=source_filter, highlight=highlight)
        elastic = Search(search_query=search_query, aggs=aggs, search_from=0, size=50,
                         idx=idx, idx_type=idx_type)
        result = elastic.search()
        mappings = elastic.get_mapping()
        context = {'data': result.docs,
                   'query': query,
                   'idx_name': idx_name,
                   'fields': search_fields,
                   'mappings': mappings,
                   'hits_total': result.hits_total}

        return render(request, 'search_engine/result.html', context,
                      content_type='text/html')
    else:
        context = {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}
        return render(request, 'search_engine/search.html', context,
                      content_type='text/html')
