''' Define region urls. '''
from django.conf.urls import url
from region import views

urlpatterns = [
    url(r'^$', views.region_page_params, name='region_page_params'),
    url(r'^(?P<region>.*)/$', views.region_page, name='region_page')
]
