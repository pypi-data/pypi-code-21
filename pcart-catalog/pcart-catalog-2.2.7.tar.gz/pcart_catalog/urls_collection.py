from django.conf.urls import url
from . import views


urlpatterns = [
    url(
        r'^$', views.collections_list_view, name='all-collections'),
    url(
        r'^(?P<collection_slug>[\d\w\-]+)/filter-form-dispatcher/$',
        views.filter_form_dispatcher,
        name='filter-form-dispatcher'),
    url(
        r'^(?P<slug>.+)/$',
        views.collection_view,
        name='product-list-for-collection'),
]
