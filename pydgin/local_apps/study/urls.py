''' Define study urls. '''
from django.conf.urls import url
from study.views import StudyView

urlpatterns = [
    url(r'^$', StudyView.as_view(), name='study_page_params'),
    url(r'^(?P<study>.*)/$', StudyView.as_view(), name='study_page')
]
