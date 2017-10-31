from django.conf.urls import url, include
from . import views

app_name = "ohm2_addresses_light"

urlpatterns = [
	url(r'^ohm2_addresses_light/$', views.index, name = 'index'),		
]


