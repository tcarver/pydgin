from django.conf.urls import url
from django.contrib import admin
from auth_test.views import index, check_section_perms, check_green, check_blue, check_yellow, check_red, check_black, \
    check_section_perms_templatetags
admin.autodiscover()


# auth_test URLs
urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^login_success/', index),
    url(r'^check_section_perms/', check_section_perms),
    url(r'^check_section_perms_templatetags/', check_section_perms_templatetags),
    url(r'^check_green/', check_green),
    url(r'^check_blue/', check_blue),
    url(r'^check_yellow/', check_yellow),
    url(r'^check_red/', check_red),
    url(r'^check_black/', check_black)
]
