from django.shortcuts import render
from elastic.search import Search, ElasticQuery, Highlight
from elastic.aggs import Agg, Aggs
from elastic.elastic_settings import ElasticSettings
from elastic.query import TermsFilter


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''
    query_dict = request.GET
    if query_dict.get("query"):
        query = query_dict.get("query")
        source_filter = ['symbol', 'synonyms', "dbxrefs.ensembl", 'biotype', 'description',
                         'pathway_name', 'id', 'journal', 'rscurrent']
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
        idx_type = ''
        elastic_attrs = ElasticSettings.attrs()
        search_idx = elastic_attrs.get('SEARCH').get('IDX_TYPES')
        if idx_name == 'ALL':
            idx = ','.join(elastic_attrs.get('IDX')[idx_name] for idx_name in search_idx.keys())
            idx_type = ','.join(itype for types in search_idx.values() for itype in types)
        else:
            idx = elastic_attrs.get('IDX')[idx_name]
            idx_type = ','.join(it for it in search_idx[idx_name])

        biotype_filter = None
        if query_dict.getlist("biotypes"):
            biotype_filter = TermsFilter.get_terms_filter("biotype", query_dict.getlist("biotypes"))

        aggs = Aggs([Agg("biotypes", "terms", {"field": "biotype", "size": 0})])
        highlight = Highlight(search_fields, pre_tags="<strong>", post_tags="</strong>", number_of_fragments=0)
        search = ElasticQuery.query_string(query, fields=search_fields, sources=source_filter,
                                           highlight=highlight, query_filter=biotype_filter)
        elastic = Search(search_query=search, aggs=aggs, search_from=0, size=50, idx=idx, idx_type=idx_type)
        result = elastic.search()
        mappings = elastic.get_mapping()
        context = {'data': result.docs, 'aggs': result.aggs,
                   'query': query, 'idx_name': idx_name,
                   'fields': search_fields, 'mappings': mappings,
                   'hits_total': result.hits_total}
        return render(request, 'search_engine/result.html', context,
                      content_type='text/html')
    else:
        context = {'index': ElasticSettings.attrs().get('SEARCH').get('IDX_TYPES').keys()}
        return render(request, 'search_engine/search.html', context,
                      content_type='text/html')
