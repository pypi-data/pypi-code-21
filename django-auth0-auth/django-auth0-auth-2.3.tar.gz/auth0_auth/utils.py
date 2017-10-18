from base64 import urlsafe_b64decode
from django.conf import settings
import json
import jwt
import logging
import requests
from urllib import urlencode


logger = logging.getLogger('auth0_auth')


DOMAIN = getattr(settings, 'AUTH0_DOMAIN')
SCOPE = getattr(settings, 'AUTH0_SCOPE', 'openid email')
RESPONSE_TYPE = getattr(settings, 'AUTH0_RESPONSE_TYPE', 'token')
CLIENT_ID = getattr(settings, 'AUTH0_CLIENT_ID')
CLIENT_SECRET = getattr(settings, 'AUTH0_CLIENT_SECRET')
SECRET_BASE64_ENCODED = getattr(settings, 'AUTH0_SECRET_BASE64_ENCODED', False)
if SECRET_BASE64_ENCODED:
    try:
        CLIENT_SECRET = urlsafe_b64decode(CLIENT_SECRET)
    except TypeError as e:
        logger.debug('Could not base64 decode client secret {}. Received error, {}.'.format(CLIENT_SECRET, e.message))


def get_login_url(domain=DOMAIN, scope=SCOPE, client_id=CLIENT_ID, redirect_uri=None, response_type=RESPONSE_TYPE, response_mode='form_post', state=None):
    param_dict = {
        'response_type': response_type,
        'response_mode': response_mode,
        'scope': scope,
        'client_id': client_id,
    }
    if redirect_uri is not None:
        param_dict['redirect_uri'] = redirect_uri
    if state is not None:
        param_dict['state'] = state
    params = urlencode(param_dict)
    return 'https://{domain}/authorize?{params}'.format(
        domain=domain,
        params=params,
    )


def get_logout_url(redirect_uri, client_id=CLIENT_ID, domain=DOMAIN):
    params = urlencode({
        'returnTo': redirect_uri,
        'client_id': client_id,
    })
    return 'https://{domain}/v2/logout?{params}'.format(
        domain=domain,
        params=params,
    )


def get_email_from_token(token=None, key=CLIENT_SECRET, audience=CLIENT_ID):
    try:
        payload = jwt.decode(token, key=key, audience=audience, leeway=300)
        if 'email' in payload:
            return payload['email']
        elif 'sub' in payload:
            return payload['sub'].split('|').pop()
        else:
            logger.debug('Could not retrieve email. Token payload does not contain keys: "email" or "sub".')
    except jwt.InvalidTokenError as e:
        logger.debug('Could not retrieve email. Token validation error, {}'.format(e.message))

    return None


def is_email_verified_from_token(token=None, key=CLIENT_SECRET, audience=CLIENT_ID):
    try:
        payload = jwt.decode(token, key=key, audience=audience, leeway=300)
        return payload.get('email_verified', True)
    except jwt.InvalidTokenError as e:
        logger.debug('Could not determine email verification status. Token validation error, {}'.format(e.message))

    return None
