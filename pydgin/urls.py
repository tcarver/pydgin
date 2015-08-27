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
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from elastic.rest_framework.api import PublicationViewSet, DiseaseViewSet,\
    MarkerViewSet

# restful framework
router = routers.DefaultRouter()
router.register(r'pubs', PublicationViewSet, base_name='pubs')
router.register(r'disease', DiseaseViewSet, base_name='disease')
router.register(r'marker', MarkerViewSet, base_name='marker')


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/', include('search_engine.urls')),
    url(r'^gene/', include('gene.urls')),
    url(r'^rest/', include(router.urls, namespace="rest")),
]
