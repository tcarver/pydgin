from django.shortcuts import render
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from elastic.elastic_settings import ElasticSettings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from django.contrib import messages
from study.document import StudyDocument


@ensure_csrf_cookie
def study_page(request, study):
    ''' Renders a study page. '''
    if study is None:
        messages.error(request, 'No study id given.')
        raise Http404()
    query = ElasticQuery(Query.ids(study.split(',')))
    elastic = Search(query, idx=ElasticSettings.idx('STUDY', 'STUDY'), size=5)
    res = elastic.search(obj_document=StudyDocument)
    if res.hits_total == 0:
        messages.error(request, 'Study(s) '+study+' not found.')
    elif res.hits_total < 9:
        names = ', '.join([getattr(doc, 'study_name') for doc in res.docs])
        context = {'features': res.docs, 'title': names}
        return render(request, 'study/study.html', context, content_type='text/html')
    raise Http404()


def study_page_params(request):
    ''' Renders a study page from GET query params. '''
    query_dict = request.GET
    return study_page(request, query_dict.get("s"))
