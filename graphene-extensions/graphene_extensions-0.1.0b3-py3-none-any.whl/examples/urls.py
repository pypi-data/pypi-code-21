from django.conf import settings
from django.conf.urls import url, include

urlpatterns = [
    url(r'restaurants', include('examples.restaurants.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
