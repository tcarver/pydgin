''' Define search engine urls. '''
from django.conf import settings
from django.conf.urls import url

from marker.views import MarkerView, MarkerViewParams, JSTestView


urlpatterns = [
    url(r'^$', MarkerViewParams.as_view(), name='marker_page_params'),
   url(r'^(?P<marker>.*)/$', MarkerView.as_view(), name='marker_page')
]

if settings.DEBUG or settings.TESTMODE:
    urlpatterns.append(url(r'^js_test/$', JSTestView.as_view(), name='js_test'))
