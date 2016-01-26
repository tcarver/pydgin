''' Define region urls. '''
from django.conf.urls import url
from disease import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.disease_page, name='disease_page'),
]
