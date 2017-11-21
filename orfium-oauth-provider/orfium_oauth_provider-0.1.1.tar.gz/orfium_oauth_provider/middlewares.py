from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from django.conf import settings

import django


def apply_auth_required_middleware(request):
    try:
        auth_required_ignore_paths = settings.AUTH_REQUIRED_IGNORE_PATHS
    except AttributeError:
        auth_required_ignore_paths = ['/accounts/', '/admin/', ]

    # ignore some pages
    for path in auth_required_ignore_paths:
        if request.path.startswith(path):
            return None

    if not request.user.is_authenticated():
        return redirect('/accounts/orfium_oauth2/login/?process=login')

    return None


# Handle changed middleware API in recent django versions
if django.VERSION[0] >= 1 and django.VERSION[1] >= 10:

    class AuthRequiredMiddleware(object):

        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            response = apply_auth_required_middleware(request)

            if response is None:
                response = self.get_response(request)

            return response

else:

    class AuthRequiredMiddleware(object):

        def process_request(self, request):
            return apply_auth_required_middleware(request)

