from django.conf.urls import url

from .views import versions_view


urlpatterns = [
    url(r'^versionz$', versions_view, name='prometheus-versions-client'),
]
