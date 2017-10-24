from django.conf import settings
from django.conf.urls import url, include
from automationcommon import views as common


urlpatterns = [
    # service status page
    url(r'^status/20d47308-dd08-4aa6-991c-c46a6e7fced7/$', common.status, name='status-page'),
]


if hasattr(settings, 'IMPERSONATION_APPS'):
    urlpatterns += [
        url(r'^hijack/', include('hijack.urls')),
        url(r'^superadmin/impersonate', common.impersonate),
    ]
