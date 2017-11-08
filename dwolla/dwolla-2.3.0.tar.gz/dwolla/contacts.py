'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all contact related endpoints.
'''

from . import constants as c
from .rest import r


def get(**kwargs):
    """
    Get contacts from user associated with OAuth token.

    :**kwargs: Additional parameters for API or client control. 
    If a "params" key with Dictionary value is passed all other 
    params in **kwargs will be discarded and only the values 
    in params used.

    :return: Dictionary with contacts.
    """
    p = {}
    kwargs_keys = kwargs.keys()
    if 'params' in kwargs:
        p = dict(list(p.items()) + list(kwargs['params'].items()))
    elif kwargs:
        for x in kwargs_keys:
            if x != 'dwollaparse' and x != 'alternate_token':
                p[x] = kwargs.pop(x)

    return r._get('/contacts', p, kwargs)


def nearby(lat, lon, **kwargs):
    """
    Returns Dwolla spots near the specified geographical location.

    :param lat: Double of latitudinal coordinates.
    :param lon: Double of longitudinal coordinates.
    :param params: Dictionary with additional parameters.

    :**kwargs: Additional parameters for API or client control. 
    If a "params" key with Dictionary value is passed all other 
    params in **kwargs will be discarded and only the values 
    in params used.
    
    :return: Dictionary with spots.
    """
    if not lat:
        raise Exception('nearby() requires lat parameter')
    if not lon:
        raise Exception('nearby() requires lon parameter')

    p = {
        'client_id': kwargs.pop('client_id', c.client_id),
        'client_secret': kwargs.pop('client_secret', c.client_secret),
        'latitude': lat,
        'longitude': lon
    }
    kwargs_keys = kwargs.keys()
    
    if 'params' in kwargs:
        p = dict(list(p.items()) + list(kwargs['params'].items()))
    elif kwargs:
        for x in kwargs_keys:
            if x != 'dwollaparse' and x != 'alternate_token':
                p[x] = kwargs.pop(x)

    return r._get_without_token('/contacts/nearby', p, kwargs)