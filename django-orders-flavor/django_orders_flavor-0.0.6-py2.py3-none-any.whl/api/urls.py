from django.conf.urls import include, url


app_name = 'orders.api'

urlpatterns = [
    url(r'^(v1/)?', include('orders.api.v1.urls', namespace='v1')),
]
