''' Define region urls. '''
from django.conf.urls import url
from region.views import RegionViewParams, RegionView


urlpatterns = [
    url(r'^$', RegionViewParams.as_view(), name='region_page_params'),
    url(r'^(?P<region>.*)/$', RegionView.as_view(), name='region_page')
]
