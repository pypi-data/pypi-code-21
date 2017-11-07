from django.conf.urls import url

from .views import StatusView

app_name = 'status'
urlpatterns = [
    url(r'^$', StatusView.as_view(), name='view'),
]
