
from django.db.models import Q
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.contrib.sites.models import Site

from seo.models import PageMeta


def _get_url_full_name(request):

    name = ''

    try:
        url = resolve(request.path_info)
    except Resolver404:
        return ''

    if url.url_name is None:
        return ''

    if url.namespaces:
        name = ':'.join(url.namespaces) + ':'

    name += url.url_name

    return name


def _get_current_url(request):
    return request.path.replace('/%s' % request.LANGUAGE_CODE, '', 1)


def get_page_meta(request, context):

    host = request.META.get('HTTP_HOST')

    try:
        site_id = Site.objects.get(domain=host)
    except Site.DoesNotExist:
        site_id = settings.SITE_ID

    try:
        page_meta = PageMeta.objects.get(
            Q(site_id=site_id) & (
                Q(url=_get_current_url(request)) |
                Q(url=_get_url_full_name(request))
            )
        )

        page_meta.compile(context)

        return page_meta

    except PageMeta.DoesNotExist:
        return None
