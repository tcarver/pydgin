from django.shortcuts import render
from elastic.search import Search, ElasticQuery, Highlight
from elastic.aggs import Agg, Aggs


def search_page(request):
    ''' Renders a page to allow searches to be constructed. '''

    idx = 'genes_hg38_v0.0.1'

    queryDict = request.GET
    if queryDict.get("query"):
        query = queryDict.get("query")
        fields = []
        for it in queryDict.items():
            if len(it) == 2:
                parts = it[1].split(":")
                if len(parts) > 1:
                    if len(parts) > 2:
                        fields.append(parts[1]+".*")
                    else:
                        fields.append(parts[1])

        aggs = Aggs(Agg("categories", "terms", {"field": "_type", "size": 0}))
        highlight = Highlight(fields)
        query = ElasticQuery.query_string(query, highlight=highlight, fields=fields)
        elastic = Search(search_query=query, aggs=aggs, search_from=0, size=20, idx=idx)
        result = elastic.search()
        context = {'data': result.docs}

        return render(request, 'search_engine/result.html', context,
                      content_type='text/html')
    else:
        search = Search(idx=idx)
        mapping = search.get_mapping()
        context = {'data': mapping[idx]}
        return render(request, 'search_engine/search.html', context,
                      content_type='text/html')
