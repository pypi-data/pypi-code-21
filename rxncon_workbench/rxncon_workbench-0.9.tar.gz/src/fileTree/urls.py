from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/$', views.file_upload, name='upload'),
    url(r'^upload/(?P<slug>[\w-]+)/$', views.file_upload, name='upload'),
    url(r'^(?P<id>\d+)/$', views.file_detail, name='detail'),
    url(r'^delete/(?P<pk>\d+)/$', views.file_delete, name="delete"),
    url(r'^compare/(?P<id>\d+)/$', views.file_compare, name="compare"),
    url(r'^delete/(?P<slug>[\w-]+)/$', views.file_delete_project, name="delete_project"),
    url(r'^load/(?P<id>\d+)/$', views.file_load, name="load"),

]
