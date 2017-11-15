from django.conf.urls import url

from views import DisMaxSearchView


urlpatterns = [
    url(r'^$', DisMaxSearchView.as_view(), name="search_view"),
]
