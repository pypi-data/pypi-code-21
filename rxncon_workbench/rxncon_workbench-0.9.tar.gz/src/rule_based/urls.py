from django.conf.urls import url

from . import views
from .views import Rule_based

urlpatterns = [
    url(r'^rule_based/$', views.rule, name='rule_based'),
    url(r'^rule_based/(?P<system_id>\d+)/$', Rule_based.as_view(), name='rule_basedCreate'),
    url(r'^delete/(?P<pk>\d+)/$', views.rule_based_delete, name="rule_basedDelete"),

]
