'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all checkouts related endpoints.
  ---------------------------------------------------------------------
  These methods only submit requests to the API, the developer is
  responsible for submitting properly formatted and correct requests.

  Further information is available on: https://docs.dwolla.com
'''

from . import constants as c
from .rest import r


def create(purchaseorder, **kwargs):
    """
    Creates an off-site gateway checkout session.

    :param purchaseorder: Dictionary with PO info, if you are passing in items you must provide them in a frozenset()
    so that they can be hashed by Python's dictionary.
    
    :**kwargs: Additional parameters for API or client control. 
    If a "params" key with Dictionary value is passed all other 
    params in **kwargs will be discarded and only the values 
    in params used.

    :return: Dictionary with URL and additional checkout response info.
    """
    if not purchaseorder:
        raise Exception('create() requires purchaseorder parameter')
    if type(purchaseorder) is dict:
        if not purchaseorder['destinationId']:
            raise Exception('purchaseorder has no destinationId key')
        if not purchaseorder['total']:
            raise Exception('purchaseorder has no total amount')
    else:
        raise Exception('create() requires purchaseorder to be of type dict')

    p = {
        'client_id': kwargs.pop('client_id', c.client_id),
        'client_secret': kwargs.pop('client_secret', c.client_secret),
        'purchaseOrder': purchaseorder
    }

    kwargs_keys = kwargs.keys()

    if 'params' in kwargs:
        p = dict(list(p.items()) + list(kwargs['params'].items()))
    elif kwargs:
        for x in kwargs_keys:
            if x != 'dwollaparse' and x != 'alternate_token':
                p[x] = kwargs.pop(x)

    id = r._post_without_token('/offsitegateway/checkouts', p, kwargs)

    if id and 'CheckoutId' in id:
        return dict(list({'URL': ((c.sandbox_host if c.sandbox else c.production_host) + 'payment/checkout/' + id['CheckoutId'])}.items()) + list(id.items()))
    else:
        raise Exception('Unable to create checkout due to API error.')

def get(cid, **kwargs):
    """
    Retrieves information (status, etc.) from an existing checkout

    :param cid: String with checkout ID

    :param kwargs: Additional parameters for client control.

    :return: Dictionary with checkout info.
    """
    if not cid:
        raise Exception('get() requires cid parameter')

    return r._get_without_token('/offsitegateway/checkouts/' + cid,
                  {
                      'client_id': kwargs.pop('client_id', c.client_id),
                      'client_secret': kwargs.pop('client_secret', c.client_secret)
                  }, kwargs)

def complete(cid, **kwargs):
    """
    Completes an offsite-gateway "Pay Later" checkout session.

    :param cid: String with checkout ID
    :return: None
    """
    if not cid:
        raise Exception('complete() requires cid parameter')

    return r._get_without_token('/offsitegateway/checkouts/' + cid + '/complete',
                  {
                      'client_id': kwargs.pop('client_id', c.client_id),
                      'client_secret': kwargs.pop('client_secret', c.client_secret)
                  }, kwargs)

def verify(sig, cid, amount, **kwargs):
    """
    Verifies offsite-gateway signature hash against
    server-provided hash.

    :param sig: String with server provided signature.
    :param cid: String with checkout ID.
    :param amount: Double with amount of checkout session.
    :return:
    """
    import hmac
    import hashlib

    if not sig:
        raise Exception('verify() requires sig parameter')
    if not cid:
        raise Exception('verify() requires cid parameter')
    if not amount:
        raise Exception('verify() requires amount parameter')

    # Normalize amount
    ampstr = '%s&%.2f' % (cid, amount)

    # Check signature
    return hmac.new(kwargs.pop('client_secret', c.client_secret), ampstr, hashlib.sha1).hexdigest() == sig






