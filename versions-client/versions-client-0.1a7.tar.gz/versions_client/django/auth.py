from __future__ import unicode_literals

from base64 import b64decode

from six import string_types

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse


def authorize(request):
    if 'HTTP_AUTHORIZATION' not in request.META:
        return False

    auth = request.META['HTTP_AUTHORIZATION'].split()
    if len(auth) != 2 or auth[0].lower() != "basic":
        return False
    username, password = b64decode(auth[1]).decode('utf-8').split(':')
    for auth in settings.VERSIONS_AUTH:
        if isinstance(auth, string_types):
            auth = auth.split(':')
        if [username, password] == list(auth):
            return True
    return False


def view_or_basicauth(view, request, *args, **kwargs):

    if authorize(request):
        return view(request, *args, **kwargs)

    response = HttpResponse(
        '401 unauthorized', status=401,
        content_type='text/plain; charset=utf-8')
    realm = getattr(settings, 'VERSIONS_REALM', 'Private section')
    response['WWW-Authenticate'] = 'Basic realm="{}"'.format(realm)
    return response


def basic(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if not settings.VERSIONS_AUTH:
                return view_func(request, *args, **kwargs)
        except AttributeError:
            raise ImproperlyConfigured('Add VERSIONS_AUTH to the settings.')
        return view_or_basicauth(view_func, request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return wrapper
