from __future__ import unicode_literals

from django.conf.urls import url

from .views import ProcessFormView

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', ProcessFormView.as_view(), name='wapps_forms_process'),
]
