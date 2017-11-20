from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.redirect_to_collections, name='all-products'),
    url(r'^(?P<product_slug>[-\w]+)/$', views.ProductDetailView.as_view(), name='product-detail'),
    url(
        r'^(?P<product_slug>[-\w]+)/(?P<variant_slug>[-\w]+)/$',
        views.ProductVariantDetailView.as_view(), name='product-variant-detail'),
]
