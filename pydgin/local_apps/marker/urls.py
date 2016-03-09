''' Define marker urls. '''
from django.conf import settings
from django.conf.urls import url

from marker import views
from marker.views import MarkerView, JSTestView


urlpatterns = [
    url(r'^$', MarkerView.as_view(), name='marker_page_params'),
    url(r'^stats/$', views.association_stats, name='assoc_stats'),
    url(r'^(?P<marker>.*)/$', MarkerView.as_view(), name='marker_page'),
]

if settings.DEBUG or settings.TESTMODE:
    urlpatterns.append(url(r'^js_test/$', JSTestView.as_view(), name='marker_js_test'))
