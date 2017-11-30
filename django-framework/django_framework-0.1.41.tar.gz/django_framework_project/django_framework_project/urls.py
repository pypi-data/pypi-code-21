from django.conf import settings
from django.conf.urls import url, include

# this helper function will automatically scan all Registered Apps in the Project
# and attempt to load their urls.py file looking for variable:  urlpatterns (must be list)
# additionally, it can be told to selectively include or exclude apps
from django_framework.django_helpers.url_helpers.load_urlpatterns import load_urlpatterns

urlpatterns = []

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


urlpatterns += load_urlpatterns()