''' Define search engine urls. '''
from django.conf.urls import url
from gene import views

urlpatterns = [
        url(r'^$', views.gene_page, name='gene_page'),
        url(r'^publications/$', views.pub_details, name='pub_details'),
    ]
