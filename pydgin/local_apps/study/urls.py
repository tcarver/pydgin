''' Define study urls. '''
from django.conf.urls import url
from study import views

urlpatterns = [
    url(r'^$', views.study_page_params, name='study_page_params'),
    url(r'^(?P<region>.*)/$', views.study_page, name='study_page')
]
