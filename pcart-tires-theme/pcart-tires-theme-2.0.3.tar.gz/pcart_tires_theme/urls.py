from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^assets/(?P<path>.*)$', views.render_asset, name='render_asset'),
]
