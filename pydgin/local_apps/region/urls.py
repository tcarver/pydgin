''' Define region urls. '''
from django.conf.urls import url
from region.views import RegionView


urlpatterns = [
    url(r'^$', RegionView.as_view(), name='region_page_params'),
    url(r'^(?P<region>.*)/$', RegionView.as_view(), name='region_page')
]
