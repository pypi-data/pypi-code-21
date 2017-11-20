from django.conf.urls import include, url
from .views import SupportLogView

urlpatterns = [
    url(r'^log/', SupportLogView.as_view(), name="support-log"),
]
