from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.styleguide, name='styleguide', kwargs={'page': 'index'}),
    url('^(?P<page>.*)/$', views.styleguide, name='styleguide'),
]
