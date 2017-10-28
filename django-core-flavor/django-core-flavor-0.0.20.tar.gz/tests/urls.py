from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [
    url(r'^v1/', include('tests.drf.urls', namespace='v1')),
    url(r'^(v2/)?', include('tests.drf.urls', namespace='v2')),
]
