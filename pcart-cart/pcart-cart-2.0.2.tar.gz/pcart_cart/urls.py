from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.cart_page_view, name='cart'),
    url(r'^add/$', views.add_to_cart, name='add-to-cart'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^checkout/shipping-form/(?P<slug>[\w\d-]+)/$', views.shipping_form, name='shipping-form'),
    url(r'^checkout/shipping-form/$', views.shipping_form, name='shipping-form-noslug'),
    url(r'^checkout/thanks/(?P<order_number>[\w\d-]+)/$', views.thanks, name='thanks'),
]
