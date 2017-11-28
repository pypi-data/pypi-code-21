
from django.conf.urls import patterns, url

from .views import ColabPautaProxyView

urlpatterns = patterns(
    '',
    url(r'^(?P<path>.*)$', ColabPautaProxyView.as_view(),
        name='colab_pauta'),
)
