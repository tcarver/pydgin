''' Define search engine urls. '''
from django.conf import settings
from django.conf.urls import url
from django.views.decorators.csrf import ensure_csrf_cookie

from gene import views
from gene.views import GeneView


urlpatterns = [
    url(r'^$', ensure_csrf_cookie(GeneView.as_view()), name='gene_page'),
    url(r'^publications/$', views.pub_details, name='pub_details'),
    url(r'^interactions/$', views.interaction_details, name='interaction_details'),
    url(r'^genesets/$', views.genesets_details, name='genesets'),
    url(r'^studies/$', views.studies_details, name='studies'),
]

if settings.DEBUG or settings.TESTMODE:
    urlpatterns.append(url(r'^js_test/$', views.js_test, name='js_test'))
