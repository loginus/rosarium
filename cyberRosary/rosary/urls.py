from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /rosary/abcdef0123456789/
    url(r'^(?P<unique_code>[0-9a-f-]+)/$', views.printout, name='printout'),
    url(r'^(?P<unique_code>[0-9a-f-]+)/check$', views.check_printout, name='check_printout'),

]
