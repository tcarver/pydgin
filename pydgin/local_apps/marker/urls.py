''' Define search engine urls. '''
from django.conf.urls import url

from marker.views import MarkerView


urlpatterns = [
        url(r'^$', MarkerView.as_view(), name='marker_page')
    ]
