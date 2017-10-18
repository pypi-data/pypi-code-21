from django.http.response import Http404
from django.utils.http import urlencode
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from django.conf import settings

from .backends import import_from


@require_http_methods(["GET"])
def authenticate_code(request):
    code = request.GET.get('code')
    if code is None:
        raise Http404('Code should have been present in request')
    else:
        user = authenticate(request=request, code=code)
        if user:
            login(request, user)
            if 'USER_POST_LOGIN_INIT' in settings.OAUTH:
                import_from(settings.OAUTH['USER_POST_LOGIN_INIT'])(request)
            return redirect(settings.OAUTH['LOGIN_COMPLETE_REDIRECT'])
        else:
            print("Not logged in")
            return redirect(settings.LOGIN_URL)


def redirect_to_login(request):
    auth_url = settings.OAUTH['AUTHORIZATION_URL']
    data = {
        'scope': 'read:user',
        'response_type': 'code',
        'redirect_uri': settings.OAUTH['REDIRECT_URI'],
        'client_id': settings.OAUTH['CLIENT_ID']
    }
    return redirect(auth_url + '?' + urlencode(data))
