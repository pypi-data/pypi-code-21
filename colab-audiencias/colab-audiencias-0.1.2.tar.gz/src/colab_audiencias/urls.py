
from django.conf.urls import patterns, url

from .views import ColabAudienciasPluginProxyView

urlpatterns = patterns(
    '',
    url(r'^(?P<path>.*)$', ColabAudienciasPluginProxyView.as_view(),
        name='colab_audiencias'),
)
