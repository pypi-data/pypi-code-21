
from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^(?P<path>.*)$', views.ColabDiscoursePluginProxyView.as_view(),
        name='colab_discourse'),
)
