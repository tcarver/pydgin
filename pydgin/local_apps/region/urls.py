''' Define region urls. '''
from django.conf.urls import url
from region.views import RegionView
from region import views


urlpatterns = [
    url(r'^$', RegionView.as_view(), name='region_page_params'),
    url(r'^criteria/$', views.criteria_details, name='criteria'),
    url(r'^(?P<region>.*)/$', RegionView.as_view(), name='region_page'),
]
