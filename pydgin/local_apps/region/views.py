from django.shortcuts import render
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from django.contrib import messages
from region.utils import Region


@ensure_csrf_cookie
def region_page(request):
    ''' Renders a region page. '''
    query_dict = request.GET
    region = query_dict.get("r")
    if region is None:
        messages.error(request, 'No region given.')
        raise Http404()
    query = ElasticQuery(Query.ids(region.split(',')))
    elastic = Search(query, idx=ElasticSettings.idx('REGION', 'REGION'), size=5)
    res = elastic.search()
    if res.hits_total == 0:
        messages.error(request, 'Region(s) '+region+' not found.')
    elif res.hits_total < 9:
        names = ', '.join([getattr(doc, 'region_name') for doc in res.docs])
        REGIONS = [Region.pad_region_doc(doc) for doc in res.docs]
        context = {'regions': REGIONS, 'title': names}
        return render(request, 'region/region.html', context, content_type='text/html')
    raise Http404()
