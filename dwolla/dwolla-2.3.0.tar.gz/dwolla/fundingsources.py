'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all funding source related endpoints.
'''

from . import constants as c
from .rest import r


def info(fid, **kwargs):
    """
    Retrieves information about a funding source by ID.

    :param fid: String of funding ID of account to retrieve information for.

    :param kwargs: Additional parameters for client control.

    :return: Dictionary with funding ID info.
    """
    if not fid:
        raise Exception('info() requires fid parameter')

    return r._get('/fundingsources/' + fid, {}, kwargs)


def get(**kwargs):
    """
    Returns a list of funding sources associated to the account
    under the current OAuth token.

    :**kwargs: Additional parameters for API or client control. 
    If a "params" key with Dictionary value is passed all other 
    params in **kwargs will be discarded and only the values 
    in params used.

    :return: Dictionary of funding sources.
    """
    p = {}
    
    kwargs_keys = kwargs.keys()
    if 'params' in kwargs:
        p = dict(list(p.items()) + list(kwargs['params'].items()))
    elif kwargs:
        for x in kwargs_keys:
            if x != 'dwollaparse' and x != 'alternate_token':
                p[x] = kwargs.pop(x)

    return r._get('/fundingsources', p, kwargs)


def add(account, routing, type, name, **kwargs):
    """
    Adds a funding source to the account under the current
    OAuth token.

    :param account: String with account number.
    :param routing: String with routing number.
    :param type: String with account type.
    :param name: String with user defined name for account.

    :param kwargs: Additional parameters for client control.

    :return: None
    """
    if not account:
        raise Exception('add() requires account parameter')
    if not routing:
        raise Exception('add() requires routing parameter')
    if not type:
        raise Exception('add() requires type parameter')
    if not name:
        raise Exception('add() requires name parameter')

    return r._post('/fundingsources',
                   {
                       'account_number': account,
                       'routing_number': routing,
                       'account_type': type,
                       'account_name': name
                   }, kwargs)


def verify(d1, d2, fid, **kwargs):
    """
    Verifies a funding source for the account associated
    with the funding ID under the current OAuth token via
    the two micro-deposits.
    :param d1: Double of first micro-deposit
    :param d2: Double of second micro-deposit
    :param fid: String with funding ID.

    :param kwargs: Additional parameters for client control.

    :return: None
    """
    if not d1:
        raise Exception('verify() requires d1 parameter')
    if not d2:
        raise Exception('verify() requires d2 parameter')
    if not fid:
        raise Exception('verify() requires fid parameter')

    return r._post('/fundingsources/' + fid,
                   {
                       'deposit1': d1,
                       'deposit2': d2
                   }, kwargs)


def withdraw(amount, fid, **kwargs):
    """
    Withdraws funds from a Dwolla account to the funding source
    associated with the passed ID, under the account associated
    with the current OAuth token.

    :param amount: Double with amount to withdraw.
    :param fid: String with funding ID to withdraw to.

    :param kwargs: Additional parameters for client control.

    :return: None
    """
    if not amount:
        raise Exception('withdraw() requires amount parameter')
    if not fid:
        raise Exception('withdraw() requires fid parameter')

    return r._post('/fundingsources/'+ fid + '/withdraw',
                   {
                       'pin': kwargs.pop('alternate_pin', c.pin),
                       'amount': amount
                   }, kwargs)


def deposit(amount, fid, **kwargs):
    """
    Deposits funds into the Dwolla account associated with the
    OAuth token from the funding ID associated with the passed
    ID.

    :param amount: Double with amount to deposit.
    :param fid: String with funding ID to deposit from.

    :param kwargs: Additional parameters for client control.

    :return: None
    """
    if not amount:
        raise Exception('deposit() requires amount parameter')
    if not fid:
        raise Exception('deposit() requires fid parameter')

    return r._post('/fundingsources/' + fid + '/deposit',
                   {
                       'pin': kwargs.pop('alternate_pin', c.pin),
                       'amount': amount
                   }, kwargs)
