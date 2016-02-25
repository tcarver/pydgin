''' Define region urls. '''
from django.conf.urls import url
from disease.views import DiseaseView, DiseaseViewParams

urlpatterns = [
    url(r'^$', DiseaseViewParams.as_view(), name='disease_page_params'),
    url(r'^(?P<disease>.*)/$', DiseaseView.as_view(), name='disease_page')
]
