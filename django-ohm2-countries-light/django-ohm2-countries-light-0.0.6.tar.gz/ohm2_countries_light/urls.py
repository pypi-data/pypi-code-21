from django.conf.urls import url, include
from . import views

app_name = "ohm2_countries_light"

urlpatterns = [
	url(r'^ohm2_countries_light/$', views.index, name = 'index'),		
]


