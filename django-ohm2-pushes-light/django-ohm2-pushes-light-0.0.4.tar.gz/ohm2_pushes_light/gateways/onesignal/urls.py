from django.conf.urls import url, include
from . import views

app_name = "onesignal"

urlpatterns = [
	url(r'^onesignal/$', views.index, name = 'index'),		
]


