from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new/$', views.quick_new, name='quick_new'),
    url(r'^(?P<id>[\w-]+)/$', views.quick_detail, name='quick_detail'),
    url(r'^compare/(?P<id>\d+)/$', views.quick_compare, name="quick_compare"),
    url(r'^delete/(?P<id>\d+)/$', views.quick_delete, name="quick_delete"),
    url(r'^(?P<id>\d+)/edit/$', views.quick_update, name='quick_update'),
    url(r'^load/(?P<id>\d+)/$', views.quick_load, name="quick_load"),
]
