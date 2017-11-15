from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^finder-form/(?P<collection_slug>[\w\d-]+)/$', views.product_finder_form, name='product-finder-form'),
]
