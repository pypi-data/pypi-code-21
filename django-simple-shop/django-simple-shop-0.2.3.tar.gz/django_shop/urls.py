from django.conf.urls import url
from django.views.decorators.csrf import ensure_csrf_cookie

from . import views


urlpatterns = [
    url(r'^shop/$',
        ensure_csrf_cookie(views.ProductCategoriesListView.as_view()),
        name='index'),
    url(r'^shop/(?P<slug>[-\w\d_]+)/$',
        ensure_csrf_cookie(views.ProductListView.as_view()),
        name='category'),
    url(r'^shop/(?P<cat_slug>[-\w\d_]+)/(?P<slug>[-\w\d_]+)/$',
        ensure_csrf_cookie(views.ProductDetailView.as_view()),
        name='product'),
    url(r'^cart/$', ensure_csrf_cookie(views.CartVerifyView.as_view()),
        name='cart'),
    url(r'^cart/checkout/$', ensure_csrf_cookie(views.CheckoutFormView.as_view()),
        name='cart_checkout'),
    url(r'^cart/modify/$', views.CartModifyFormView.as_view(),
        name='cart_modify'),
    url(r'^order/(?P<uuid>[\w\d]{32})/$', views.OrderView.as_view(),
        name='order'),
]
