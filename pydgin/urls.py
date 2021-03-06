"""pydgin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.views.static import serve
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from core.rest_framework.rest_api import LocationsViewSet, FeatureViewSet
from marker.rest_framework.rest_api import LDViewSet, PopulationsViewSet
from region.rest_framework.rest_api import DiseaseRegionViewSet
from study.views import StudiesEntryView
from pydgin import views, rest_api
from criteria.rest_framework.rest_api import CriteriaViewSet


# restful framework
router = routers.DefaultRouter()
router.register(r'pubs', rest_api.PublicationViewSet, base_name='pubs')
router.register(r'ld', LDViewSet, base_name='ld')
router.register(r'populations', PopulationsViewSet, base_name='populations')
router.register(r'locations', LocationsViewSet, base_name='locations')
router.register(r'features', FeatureViewSet, base_name='features')
router.register(r'regions', DiseaseRegionViewSet, base_name='regions')
router.register(r'criteria', CriteriaViewSet, base_name='criteria')

urlpatterns = [
    url(r'^{}/admin/'.format(settings.ADMIN_URL_PATH), include(admin.site.urls)),
    url(r'^accounts/', include('pydgin_auth.urls', namespace="accounts")),
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^terms/', views.terms, name='terms'),
    url(r'^faq/', views.faq, name='faq'),
    url(r'^data_source/', views.data_source, name='data_source'),
    url(r'^contact', views.contact, name='contact'),
    # url(r'^browser/', include('browser.urls')),
    url(r'^search/', include('search_engine.urls')),
    url(r'^gene/', include('gene.urls')),
    url(r'^region/', include('region.urls')),
    url(r'^study/', include('study.urls')),
    url(r'^studies/$', StudiesEntryView.as_view(), name='studies'),
    url(r'^disease/', include('disease.urls')),
    url(r'^marker/', include('marker.urls')),
    url(r'^rest/', include(router.urls, namespace="rest")),
    url(r'^rest-docs/', include('rest_framework_swagger.urls')),
    url(r'^api-token-auth/', obtain_auth_token),
    url(r'^jbrowse/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT+'/jbrowse/'}),
    url(r'^criteria_tool/', include('criteria.urls')),

]
