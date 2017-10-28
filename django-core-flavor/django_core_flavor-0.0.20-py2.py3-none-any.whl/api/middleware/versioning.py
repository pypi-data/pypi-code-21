import re

from django.conf import settings
from django.http import Http404

from django.urls import resolve, reverse, NoReverseMatch
from django.urls.exceptions import Resolver404

from django.utils.translation import ugettext_lazy as _


class VersioningMiddleware(object):
    X_MEDIA_TYPE = "X-{site}-Media-Type".format(
        site=settings.SITE_NAME.title())

    MEDIA_TYPE_PATTERN = re.compile(
        r"application/vnd.{}(?P<sandbox>.sandbox)?"
        r".(?P<version>v\d+)\+(?P<format>\w+)"
        .format(settings.SITE_NAME))

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        media_type = self.get_media_type(request)
        request.version = self.get_url_version(request)

        # media-type header?
        if media_type is not None:
            request.format = media_type['format']
            request.sandbox = media_type['sandbox']

            if request.format == 'api':
                request.META['HTTP_ACCEPT'] = 'text/html'
            else:
                request.META['HTTP_ACCEPT'] =\
                    "application/{}".format(request.format)

            # not url versioning -> redirect to media-type version
            if request.version is None:
                request.version = media_type['version']
                request.path_info = self.get_path_info(request)
        else:
            request.format = request.GET.get('format')
            request.sandbox = request.GET.get('sandbox') == '1'

        response = self.get_response(request)
        response[self.X_MEDIA_TYPE] = self.get_response_media_type(request)
        return response

    @classmethod
    def resolve(cls, request):
        if hasattr(request, 'host'):
            urlconf = request.host.urlconf
        else:
            urlconf = None

        try:
            return resolve(request.path_info, urlconf=urlconf)
        except Resolver404:
            return None

    @classmethod
    def reverse(cls, request, view_name, **kwargs):
        if hasattr(request, 'host'):
            from django_hosts import reverse as reverse_host
            return reverse_host(view_name, host=request.host.name, **kwargs)[
                len(request.host.name) + 2:
            ]
        return reverse(view_name, **kwargs)

    @classmethod
    def get_path_info(cls, request, regex_version=re.compile(r'v\d+')):
        url_resolver = cls.resolve(request)

        if url_resolver is not None:
            namespaces = url_resolver.view_name.split(':')

            for index, namespace in enumerate(url_resolver.namespaces):
                if regex_version.match(namespace) is not None:
                    namespaces[index] = request.version
                    try:
                        return cls.reverse(
                            request,
                            view_name=':'.join(namespaces),
                            kwargs=url_resolver.kwargs
                        )
                    except NoReverseMatch:
                        raise Http404(_('Version not found'))

        # 404 not found OR standalone view
        return request.path_info

    @classmethod
    def get_media_type(cls, request):
        media_type = request.META.get('HTTP_ACCEPT', '')
        match = cls.MEDIA_TYPE_PATTERN.match(media_type)

        if match is not None:
            fields = match.groupdict()
            fields['sandbox'] = bool(fields['sandbox'])
            return fields
        return None

    @classmethod
    def get_response_media_type(cls, request):
        return "{site}{sandbox}.{version}; format={format}".format(
            site=settings.SITE_NAME,
            sandbox='.sandbox' if request.sandbox else '',
            version=request.version or '?',
            format=request.format or '?')

    @classmethod
    def get_url_version(cls, request, regex_version=re.compile(r'v\d+')):
        url_resolver = cls.resolve(request)

        if url_resolver is not None:
            return next((
                namespace for namespace in url_resolver.namespaces
                if regex_version.match(namespace) is not None
            ), None)
        return None
