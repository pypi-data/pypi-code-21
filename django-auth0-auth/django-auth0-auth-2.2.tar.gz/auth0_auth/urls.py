from .views import auth, callback, logout
from django.conf.urls import url


urlpatterns = [
    url(r'^login/$', auth, name='auth0_login'),
    url(r'^logout/$', logout, name='auth0_logout'),
    url(r'^callback/$', callback, name='auth0_callback'),
]
