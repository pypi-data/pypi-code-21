from django.conf.urls import url

from . import views
from .views import Bool

urlpatterns = [
    url(r'^boolnet/$', views.bool, name='boolnet'),
    url(r'^boolnet/(?P<system_id>\d+)/$', Bool.as_view(), name='boolnetCreate'),
    url(r'^delete/(?P<pk>\d+)/$', views.bool_delete, name="boolnetDelete"),

]
