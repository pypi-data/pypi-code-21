from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^orders/(?P<pk>[0-9a-f]{32})/paypal-form$',
        views.PaypalOrderFormView.as_view(),
        name='item-paypal-form'),

    url(r'^api/', include('orders.api.urls', namespace='api'))
]
