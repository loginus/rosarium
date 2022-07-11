# from django.conf.urls import url
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    # ex: /rosary/abcdef0123456789/
    re_path(r'^(?P<unique_code>[0-9a-f-]+)/$', views.printout, name='printout'),
    re_path(r'^(?P<unique_code>[0-9a-f-]+)/check$', views.check_printout, name='check_printout'),
    re_path(r'^all$', views.full_printout, name='full_printout'),
]
