from .backends import Auth0Backend
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, resolve_url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import logging
from urlparse import urlparse
import uuid


logger = logging.getLogger('auth0_auth')


@never_cache
def auth(request):
    backend = Auth0Backend()
    redirect_uri = request.build_absolute_uri(reverse(callback))
    state = str(uuid.uuid4())
    request.session['state'] = state
    login_url = backend.login_url(
        redirect_uri=redirect_uri,
        state=state,
    )
    return HttpResponseRedirect(login_url)


@never_cache
def logout(request):
    backend = Auth0Backend()
    logout_redirect_url = getattr(settings, 'LOGOUT_REDIRECT_URL', '/')
    redirect_uri = request.build_absolute_uri(resolve_url(logout_redirect_url))
    logout_url = backend.logout_url(
        redirect_uri=redirect_uri,
    )
    auth_logout(request)
    return HttpResponseRedirect(logout_url)


@never_cache
@csrf_exempt
def callback(request):
    backend = Auth0Backend()
    original_state = request.session.get('state')
    state = request.POST.get('state')
    if original_state == state:
        token = request.POST.get('id_token')
        logger.debug('Token {} received'.format(token))
        user = backend.authenticate(token=token)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(get_login_success_url(request))
    else:
        logger.debug('Expected state {} but received {}.'.format(original_state, state))
    return redirect('auth0_login')


def get_login_success_url(request):
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')
    netloc = urlparse(redirect_to)[1]
    if not redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    elif netloc and netloc != request.get_host():
        redirect_to = settings.LOGIN_REDIRECT_URL
    return redirect_to
