from django.conf.urls import url

from . import views
from .views import ReaGraph
from .views import SReaGraph

urlpatterns = [
    url(r'^regGraph/$', views.regGraph, name='regGraph'),
    url(r'^regGraphFile/(?P<system_id>\d+)/$', views.regGraphFile, name='regGraphCreateFromFile'),
    url(r'^regGraphQuick/(?P<system_id>\d+)/$', views.regGraphQuick, name='regGraphCreateFromQuick'),
    url(r'^reaGraph/$', views.reaGraph, name='reaGraph'),
    url(r'^reaGraph/(?P<system_id>\d+)/$', ReaGraph.as_view(), name='reaGraphCreate'),
    url(r'^sReaGraph/$', views.sReaGraph, name='sReaGraph'),
    url(r'^sReaGraph/(?P<system_id>\d+)/$', SReaGraph.as_view(), name='sReaGraphCreate'),
    url(r'^delete/(?P<pk>\d+)/$', views.graph_delete, name="delete"),
]
