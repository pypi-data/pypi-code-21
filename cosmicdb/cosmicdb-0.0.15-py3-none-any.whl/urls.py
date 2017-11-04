from django.contrib import admin
from django.conf import settings
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout, \
    password_change_done, password_reset_done, password_reset_complete

from cosmicdb.views import CosmicLoginView, CosmicSignupView, CosmicPasswordResetView, \
    CosmicPasswordResetConfirmView, CosmicPasswordChangeView, \
    Home, Dashboard, notifications, messages

favicon_view = RedirectView.as_view(url=static('cosmicdb/img/favicon.ico'), permanent=True)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', CosmicLoginView.as_view(), name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^password_change/$', CosmicPasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change_done/$', password_change_done, name='password_change_done'),
    url(r'^password_reset/$', CosmicPasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset_done/$', password_reset_done, name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',CosmicPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^password_reset_complete/$', password_reset_complete, name='password_reset_complete'),
    url(r'^favicon\.ico$', favicon_view, name='favicon_default'),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^dashboard/$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^notifications/$', notifications, name='notifications'),
    url(r'^notifications/(?P<id>[0-9]+)/$', notifications, name='notifications'),
    url(r'^messages/$', messages, name='messages'),
    url(r'^messages/(?P<id>[0-9]+)/$', messages, name='messages'),
]

if hasattr(settings, 'COSMICDB_ALLOW_SIGNUP'):
    if settings.COSMICDB_ALLOW_SIGNUP:
        urlpatterns = urlpatterns + [
            url(r'^signup/$', CosmicSignupView.as_view(), name='signup'),
        ]
