''' Define region urls. '''
from django.conf.urls import url
from region import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.region_page, name='region_page'),
]
