from django.conf.urls import *

from . import views

urlpatterns = (
    url(r'^wlogin/', views.wlogin, name='wlogin'),
    url(r'^wlogged/$', views.wlogged, name='wlogged'),
    url(r'', include('social_django.urls')),
)