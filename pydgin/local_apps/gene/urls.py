''' Define search engine urls. '''
from django.conf.urls import url
from gene import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.gene_page_params, name='gene_page_params'),
    url(r'^publications/$', views.pub_details, name='pub_details'),
    url(r'^interactions/$', views.interaction_details, name='interaction_details'),
    url(r'^genesets/$', views.genesets_details, name='genesets'),
    url(r'^studies/$', views.studies_details, name='studies'),
    url(r'^(?P<gene>ENSG\d+)/$', views.gene_page, name='gene_page')
]

if settings.DEBUG or settings.TESTMODE:
    urlpatterns.append(url(r'^js_test/$', views.js_test, name='js_test'))
