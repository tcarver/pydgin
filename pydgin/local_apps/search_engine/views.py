from django.shortcuts import render
from elastic.search import Search, ElasticQuery, Highlight
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from pydgin_auth.permissions import check_index_perms


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''

    queryDict = request.GET

    idx_names = ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()
    # manage the permissions here..check if user is in READ group to read indexes
    idx_names_auth = check_index_perms(request.user, idx_names)
    idx_names = idx_names_auth

    if queryDict.get("query"):
        query = queryDict.get("query")
        source_filter = ['symbol', 'synonyms', "dbxrefs.ensembl", 'biotype', 'description',
                         'pathway_name', 'id', 'journal', 'rscurrent', 'interactors', 'interaction_source']
        search_fields = []

        for it in queryDict.items():
            if len(it) == 2:
                if it[0] == 'query':
                    continue
                parts = it[1].split(":")
                if len(parts) > 1:
                    if len(parts) == 3:
                        search_fields.append(parts[1]+"."+parts[2])
                    elif len(parts) == 2:
                        search_fields.append(parts[1])

        if len(search_fields) == 0 and not (isinstance(query, int) or query.isdigit()):
            search_fields = list(source_filter)
            search_fields.extend(['abstract', 'title', 'authors.name', 'pmids', 'gene_sets', 'interactor'])

        source_filter.extend(['pmid', 'build_id'])

        idx_name = queryDict.get("idx")
        idx_type = ''

        if idx_name == 'ALL':
            type_arrs = ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').values()

            idx = ','.join(ElasticSettings.attrs().get('IDX')[idx_name] for idx_name in idx_names)
            idx_type = ','.join(itype for types in type_arrs for itype in types)
        else:
            if idx_name in idx_names_auth:
                idx = ElasticSettings.attrs().get('IDX')[idx_name]
                idx_type = ','.join(it for it in ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES')[idx_name])

        aggs = Aggs(Agg("categories", "terms", {"field": "_type", "size": 0}))
        highlight = Highlight(search_fields, pre_tags="<strong>", post_tags="</strong>", number_of_fragments=0)
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
        context = {'index': idx_names_auth}
        return render(request, 'search_engine/search.html', context,
                      content_type='text/html')
