from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from .registrations import views

urlpatterns = [
    # Example:
    # (r'^cross_triangulaire/', include('cross_triangulaire.foo.urls')),
    url(r'^register/$', views.register, name='register'),
    url(r'^list/$', views.list_participants, name='list'),
    url(r'^listall/$', views.list_participants_full, name='listall'),
    url(r'^access/$', views.access, name='access'),
    url(r'^$', views.index, name='index'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'registrations/login.html'}),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]
