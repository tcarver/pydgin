''' Define study urls. '''
from django.conf.urls import url
from study.views import StudyViewParams, StudyView

urlpatterns = [
    url(r'^$', StudyViewParams.as_view(), name='study_page_params'),
    url(r'^(?P<study>.*)/$', StudyView.as_view(), name='study_page')
]
