
from django.conf.urls import patterns, url
from django.views.decorators.clickjacking import xframe_options_exempt

from .views import ColabWikilegisPluginProxyView


urlpatterns = patterns(
    '',
    url(r'^(?P<path>.*)$',
        xframe_options_exempt(ColabWikilegisPluginProxyView.as_view()),
        name='colab_wikilegis'),
)
