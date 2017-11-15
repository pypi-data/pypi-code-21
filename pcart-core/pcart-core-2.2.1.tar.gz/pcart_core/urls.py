from django.conf.urls import url
from . import views


urlpatterns = [
    url(
        r'^system-info/$',
        views.pcart_system_info_view,
        name='pcart-admin-system-info'),
    url(
        r'^clear-cache/$',
        views.pcart_clear_cache_view,
        name='pcart-admin-clear-cache'),
]
