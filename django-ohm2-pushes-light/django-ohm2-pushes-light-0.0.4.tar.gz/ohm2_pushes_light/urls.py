from django.conf.urls import url, include
from . import views

app_name = "ohm2_pushes_light"

urlpatterns = [
	url(r'^api/v1/', include('ohm2_pushes_light.api.v1.urls', namespace = "api_v1")),
]


