import re

from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.views.static import serve
from wagtail.contrib.wagtailsitemaps.views import sitemap
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls

import coop.styleguide.urls


def asset_redirect(src, dest):
    try:
        asset_url = staticfiles_storage.url(dest)
    except ValueError:
        def view(request):
            raise Http404
    else:
        def view(request):
            return HttpResponsePermanentRedirect(asset_url)
    return url('^' + re.escape(src) + '$', view)


def handler404(request, exception=None):
    request.is_preview = False
    return render(request, 'layouts/404.html', {'exception': exception}, status=404)


def handler500(request):
    request.is_preview = False
    return render(request, 'layouts/500.html', status=500)


urlpatterns = [
    asset_redirect('favicon.ico', 'images/favicon.png'),
    asset_redirect('humans.txt', 'misc/humans.txt'),
    asset_redirect('robots.txt', 'misc/robots.txt'),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^sitemap\.xml$', sitemap),
    url(r'^_styleguide/', include(coop.styleguide.urls)),
    url(r'^404/$', handler404),
    url(r'^500/$', handler500),
    url(r'', include(wagtail_urls)),
]


if settings.DEBUG or getattr(settings, 'FORCE_ASSET_SERVING', False):
    def static(prefix, document_root):
        pattern = r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/'))
        return [url(pattern, serve, kwargs={'document_root': document_root})]
    urlpatterns += static(settings.STATIC_URL, settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, settings.MEDIA_ROOT)
