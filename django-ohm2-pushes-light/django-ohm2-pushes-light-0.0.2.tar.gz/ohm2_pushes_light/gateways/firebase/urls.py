from django.conf.urls import url, include
from . import views

app_name = "firebase"

urlpatterns = [
	url(r'^firebase/$', views.index, name = 'index'),		
]


