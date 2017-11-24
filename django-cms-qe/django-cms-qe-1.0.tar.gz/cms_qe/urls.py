"""
URL Configuration
https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.i18n import JavaScriptCatalog

from . import views

__all__ = (
    'handler403',
    'handler404',
    'handler500',
    'handler503',
    'urlpatterns',
)

# pylint: disable=invalid-name
handler403 = 'cms_qe.views.handler403'
handler404 = 'cms_qe.views.handler404'
handler500 = 'cms_qe.views.handler500'
handler503 = 'cms_qe.views.handler503'

urlpatterns = [
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^', include('filer.server.urls')),
    url(r'^csp-report', views.csp_report),
    url(r'^', include('cms_qe_table.urls')),
    url(r'^', include('cms_qe_newsletter.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'api/monitoring', views.get_monitoring),
]


# During development is error page replaced by Django error page with debug info.
# This is registration special URLs for testing error pages in dev mode.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^403/$', views.handler403),
        url(r'^404/$', views.handler404),
        url(r'^503/$', views.handler503),
    ]

# Django CMS has to be the last one because it will consume all URLs.
urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('cms_qe_auth.urls')),
    url(r'^', include('cms.urls')),
)
