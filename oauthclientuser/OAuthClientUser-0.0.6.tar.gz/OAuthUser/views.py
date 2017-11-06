# -*- coding: utf-8 -*-
import json
import random
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model, login, logout
from django.http.response import HttpResponseRedirect, HttpResponse
from django.http.response import HttpResponseForbidden
from rest_framework.exceptions import AuthenticationFailed

from .http_utils import post_request, get_account_info
from .models import TUserExtra


logger = logging.getLogger(__name__)


# Create your views here.
def api_oauth_login_view(request):
    params = {
        'state': ''.join([random.choice('1234567890') for i in range(12)]),
        'client_id': settings.OAUTH_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.OAUTH_REDIRECT_URI
    }

    params = '&'.join(['{}={}'.format(k, v) for k, v in params.items()])

    url = '{}?{}'.format(settings.OAUTH_AUTHENTICATE_URL, params)

    return HttpResponseRedirect(url)


def api_oauth_logout_view(request):
    logout(request)
    return HttpResponseRedirect(settings.BASE_URL)


def api_oauth_granted_view(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    params = {
        'grant_type': settings.OAUTH_AUTHENTICATE_TYPE,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'code': code
    }

    status, response = post_request(
        settings.OAUTH_TOKEN_URL,
        params,
        settings.OAUTH_CLIENT_ID,
        settings.OAUTH_CLIENT_SECRET)

    if status != 200:
        return HttpResponseForbidden()

    data = json.loads(response)

    status, response = get_account_info(settings.OAUTH_ACCOUNT_URL, data.get('token_type'), data.get('access_token'))
    if status != 200:
        return HttpResponseForbidden()

    account_info = json.loads(response)
    privilege_list = account_info.get('privileges', [])
    if hasattr(settings, 'OAUTH_CLIENT_PRIVILEGE_REQUIRED') and settings.OAUTH_CLIENT_PRIVILEGE_REQUIRED not in privilege_list:
        raise AuthenticationFailed('You have no permission to access the service.')

    username = account_info.get('username')

    user_model = get_user_model()

    try:
        user = user_model.objects.select_related('extra').get(username=username)
    except ObjectDoesNotExist:
        user = user_model.objects.create(username=username)

    if not hasattr(user, 'extra'):
        TUserExtra.objects.create(
            user=user,
            phone_number=account_info.get('mobile'),
            access_token=data.get('access_token'),
            token_type=data.get('token_type'),
            scope=data.get('scope'),
            expires_in=data.get('expires_in'),
            refresh_token=data.get('refresh_token'),
            remote_privileges='|'.join(account_info.get('privileges', [])))
    else:
        user.extra.access_token = data.get('access_token')
        user.extra.token_type = data.get('token_type')
        user.extra.scope = data.get('scope')
        user.extra.expires_in = data.get('expires_in')
        user.extra.refresh_token = data.get('refresh_token')
        user.extra.remote_privileges = '|'.join(account_info.get('privileges', []))
        user.extra.save()

    login(request, user)

    return HttpResponseRedirect(settings.BASE_URL)
