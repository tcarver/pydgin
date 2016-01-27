''' Define region urls. '''
from django.conf.urls import url
from disease import views

urlpatterns = [
    url(r'^$', views.disease_page_params, name='disease_page_params'),
    url(r'^(?P<disease>.*)/$', views.disease_page, name='disease_page')
]
