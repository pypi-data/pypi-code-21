
from django.db.models import Q
from django.core.urlresolvers import resolve, Resolver404

from misc.utils import get_site_id_from_request

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

    try:
        page_meta = PageMeta.objects.get(
            Q(site_id=get_site_id_from_request(request)) & (
                Q(url=_get_current_url(request)) |
                Q(url=_get_url_full_name(request))
            )
        )

        page_meta.compile(context)

        return page_meta

    except PageMeta.DoesNotExist:
        return None
