from django.conf.urls import url

from . import views

urlpatterns = [url(r'^parser/', views.parser, name='django-om-parser')]
