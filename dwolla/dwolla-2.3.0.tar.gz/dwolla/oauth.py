'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all OAuth related endpoints.
'''

from . import constants as c
from .rest import r


def genauthurl(**kwargs):
    """
    Returns an OAuth permissions page URL. If no redirect is set,
    the redirect in the Dwolla Application Settings will be use
    If no scope is set, the scope in the settings object will be use

    :param redirect: String with redirect destination.
    :param scope: OAuth scope string to override default scope in settings object.

    :**kwargs: Additional parameters for API or client control. 

    :return: String with URL
    """
    try:
        from urllib.parse import quote
    except ImportError:
        from urllib import quote

    return (c.sandbox_host if c.sandbox else c.production_host) \
        + 'oauth/v2/authenticate?client_id=' \
        + quote(kwargs.pop('client_id', c.client_id)) \
        + '&response_type=code&scope=' \
        + kwargs.pop('scope', c.oauth_scope) \
        + (('&redirect_uri=' + quote(kwargs.pop('redirect'))) if 'redirect' in kwargs else '') \
        + ('&verified_account=' + quote(kwargs.pop('verified_account')) if 'verified_account' in kwargs else '')


def get(code, **kwargs):
    """
    Returns an OAuth token + refresh pair in an array. If no redirect
    is set, the redirect in the Dwolla Application Settings will be use

    :param code: Code from redirect response.
    :param redirect: String with redirect destination.

    :**kwargs: Additional parameters for API or client control. 

    :return: Dictionary with access and refresh token pair.
    """
    if not code:
        raise Exception('get() requires code parameter')

    p = {
        'client_id': kwargs.pop('client_id', c.client_id),
        'client_secret': kwargs.pop('client_secret', c.client_secret),
        'grant_type': 'authorization_code',
        'code': code
    }

    if 'redirect' in kwargs:
        p['redirect_uri'] = kwargs.pop('redirect')

    return r._post_without_token('/token/', p, kwargs, custompostfix='/oauth/v2')

def refresh(refreshtoken, **kwargs):
    """
    Returns a newly refreshed access token and refresh token pair.

    :param refreshtoken: String with refresh token from initial OAuth handshake.

    :param kwargs: Additional parameters for client control.

    :return: Dictionary with access and refresh token pair.
    """
    if not refreshtoken:
        raise Exception('refresh() requires refreshtoken parameter')

    p = {
        'client_id': kwargs.pop('client_id', c.client_id),
        'client_secret': kwargs.pop('client_secret', c.client_secret),
        'grant_type': 'refresh_token',
        'refresh_token': refreshtoken
    }

    return r._post_without_token('/token/', p, kwargs, custompostfix='/oauth/v2')

def catalog(**kwargs):
    """
    Returns a "catalog" of endpoints that are available for use
    with the current/passed OAuth token.

    :param alternate_token: String with OAuth token to override value in constants

    :param kwargs: Additional parameters for client control.
    
    :return Dictionary with catalog of endpoints and their URLs.
    """
    return r._get('/catalog', {}, kwargs)['_links']

