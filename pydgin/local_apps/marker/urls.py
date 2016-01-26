''' Define search engine urls. '''
from django.conf.urls import url
from marker import views

urlpatterns = [
    url(r'^$', views.marker_page_params, name='marker_page_params'),
    url(r'^(?P<marker>.*)/$', views.marker_page, name='marker_page'),
    url(r'^ld_search/$', views.ld_search, name='ld_search'),
]
