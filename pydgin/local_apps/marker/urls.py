''' Define search engine urls. '''
from django.conf import settings
from django.conf.urls import url

from marker import views
from marker.views import MarkerView


urlpatterns = [
        url(r'^$', MarkerView.as_view(), name='marker_page')
    ]

if settings.DEBUG or settings.TESTMODE:
    urlpatterns.append(url(r'^js_test/$', views.js_test, name='js_test'))
