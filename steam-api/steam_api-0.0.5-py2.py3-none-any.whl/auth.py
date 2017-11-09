import requests
import re

# compatibility import url encode fn?
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

#: steam open id login url
STEAM_LOGIN_URL = 'http://steamcommunity.com/openid/login'


def get_login_url(redirect_url):
    """
    Return login url to client

    :param redirect_url: redirect url when logged successfully
    :return: steam login url

    Example

    .. code-block:: python

       import steam_api
       redirect_url = 'http://localhost'
       url = stem_api.auth.get_login_url(redirect_url)

       # render `url` as hyperlink, and click url to login
       render('<a href={link}>login</a>'.format(link=url))
    """

    auth_parameters = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": redirect_url,
        "openid.realm": redirect_url,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select"
    }

    return "{0}?{1}".format(
        STEAM_LOGIN_URL,
        urlencode(auth_parameters))


def get_steam_id(**results):
    """
    TODO: exchange steam_id with params returned from steam openid

    :param results:
    :return:

    Example

    .. code-block:: python

       res = steam_api.auth.get_steam_id(**request.args)

       {
         'valid': True,
         'id: 'steam_id'
       }

       or

       {
         'valid': False
       }
    """
    validation_args = {
        'openid.assoc_handle': results['openid.assoc_handle'][0],
        'openid.signed': results['openid.signed'][0],
        'openid.sig': results['openid.sig'][0],
        'openid.ns': results['openid.ns'][0]
    }

    # Basically, we split apart one of the args steam sends back only to send it back to them to validate!
    # We also append check_authentication which tells OpenID 2 to actually yknow, validate what we send.
    signed_args = results['openid.signed'][0].split(',')

    for item in signed_args:
        item_arg = 'openid.{0}'.format(item)
        if results[item_arg][0] not in validation_args:
            validation_args[item_arg] = results[item_arg][0]

    validation_args['openid.mode'] = 'check_authentication'

    # Just use requests to quickly fire the data off.
    res = requests.post(STEAM_LOGIN_URL, data=validation_args)

    # is_valid:true is what Steam returns if something is valid.
    # The alternative is is_valid:false which obviously, is false.

    if re.search('is_valid:true', res.text):
        matched_64id = re.search('http://steamcommunity.com/openid/id/(\d+)', results['openid.claimed_id'][0])
        if matched_64id is not None or matched_64id.group(1) is not None:
            return {
                'valid': True,
                'id': matched_64id.group(1)
            }
        else:
            # If we somehow fail to get a valid steam64ID, just return false
            return {'valid': False}
    else:
        # Same again here
        return {'valid': False}
