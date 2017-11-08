'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all webhooks related endpoints.
  ---------------------------------------------------------------------
  These methods only submit requests to the API, the developer is
  responsible for submitting properly formatted and correct requests.

  Further information is available on: https://docs.dwolla.com
'''

from . import constants as c


def verify(sig, body):
    """
    Verifies webhook signature hash against
    server-provided hash.

    :param sig: String with server provided signature.
    :param body: request body.
    :return:
    """
    if not sig:
        raise Exception('verify() requires sig parameter')
    if not body:
        raise Exception('verify() requires body parameter')
    import hmac
    import hashlib

    return hmac.new(c.client_secret, body, hashlib.sha1).hexdigest() == sig

