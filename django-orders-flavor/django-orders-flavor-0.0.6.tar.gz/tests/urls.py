from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('orders.api.urls', namespace='orders-api')),
    url(r'^paypal/', include('paypal.standard.ipn.urls'))
]
