import json
import time
try:
  import urllib.parse as urlparse
except ImportError:
  import urllib as urlparse

import base64
import hashlib
import hmac

import requests


ITBIT_BASE_URL = 'https://api.itbit.com/v1'


class MessageSigner(object):

  def make_message(self, verb, url, body, nonce, timestamp):
    # There should be no spaces after separators
    return json.dumps([verb, url, body, str(nonce), str(timestamp)], separators=(',', ':'))

  def sign_message(self, secret, verb, url, body, nonce, timestamp):
    message = self.make_message(verb, url, body, nonce, timestamp)
    sha256_hash = hashlib.sha256()
    nonced_message = str(nonce) + message
    sha256_hash.update(nonced_message.encode('utf8'))
    hash_digest = sha256_hash.digest()
    hmac_digest = hmac.new(secret, url.encode('utf8') + hash_digest, hashlib.sha512).digest()
    return base64.b64encode(hmac_digest)


class itBit(object):
  def __init__(self, clientKey=None, secret=None, userId=None):
    '''
    clientKey, secret, and userId are provided by itBit and are specific to your user account
    '''
    self.clientKey = clientKey
    self.secret = secret.encode('utf-8') if secret else None
    self.userId = userId
    self.nonce = 0

  def get_ticker(self, tickerSymbol='XBTUSD'):
    '''
    returns ticker information for a specific ticker symbol
    '''
    path = '/markets/%s/ticker' % (tickerSymbol)
    response = self.make_request('GET', path, {})
    return response

  def get_order_book(self, tickerSymbol='XBTUSD'):
    '''
    returns order book information for a specific ticker symbol
    '''
    path = '/markets/%s/order_book' % (tickerSymbol)
    response = self.make_request('GET', path, {})
    return response

  def get_all_wallets(self, filters={}):
    '''
    returns a list of all wallets for the userid provided
    '''
    filters['userId'] = self.userId
    queryString = self._generate_query_string(filters)
    path = '/wallets%s' % (queryString)
    response = self.make_request('GET', path, {})
    return response

  def create_wallet(self, walletName):
    '''
    creates a new wallet
    '''
    path = '/wallets'
    response = self.make_request('POST', path, {'userId': self.userId, 'name': walletName})
    return response

  def get_wallet(self, walletId):
    '''
    returns a specific wallet by wallet id
    '''
    path = '/wallets/%s' % (walletId)
    response = self.make_request('GET', path, {})
    return response

  def get_wallet_balance(self, walletId, currency):
    '''
    returns the balance of a specific currency within a wallet
    '''
    path = '/wallets/%s/balances/%s' % (walletId, currency)
    response = self.make_request('GET', path, {})
    return response

  def get_wallet_trades(self, walletId, filters={}):
    '''
    returns a list of trades for a specific wallet
    results are paginated and limited to a maximum of 50 per request
    '''
    queryString = self._generate_query_string(filters)
    path = '/wallets/%s/trades%s' % (walletId, queryString)
    response = self.make_request('GET', path, {})
    return response

  def get_funding_history(self, walletId, filters={}):
    '''
    returns a list of funding history for a wallet  
    response will be paginated and limited to 50 items per response
    '''
    queryString = self._generate_query_string(filters)
    path = '/wallets/%s/funding_history%s' % (walletId, queryString)
    response = self.make_request('GET', path, {})
    return response

  def get_wallet_orders(self, walletId, filters={}):
    '''
    returns a list of orders for a wallet 
    response will be paginated and limited to 50 items per response  
    orders can be filtered by status (ex: open, filled, etc)
    '''
    queryString = self._generate_query_string(filters)
    path = '/wallets/%s/orders%s' % (walletId, queryString)
    response = self.make_request('GET', path, {})
    return response

  def create_order(self, walletId, side, currency, amount, price, instrument):
    '''
    creates a new limit order
    '''
    path = '/wallets/%s/orders/' % (walletId)
    response = self.make_request('POST', path, {'type': 'limit', 'currency': currency, 'side': side, 'amount': amount, 'price': price, 'instrument': instrument})
    return response

  def create_order_with_display(self, walletId, side, currency, amount, price, display ,instrument):
    '''
    creates a new limit order with a specific display amount (iceberg order)
    '''
    path = '/wallets/%s/orders/' % (walletId)
    response = self.make_request('POST', path, {'type': 'limit', 'currency': currency, 'side': side, 'amount': amount, 'price': price, 'display': display, 'instrument': instrument})
    return response

  def get_order(self, walletId, orderId):
    '''
    returns a specific order by order id
    '''
    path = '/wallets/%s/orders/%s' % (walletId, orderId)
    response = self.make_request('GET', path, {})
    return response

  def cancel_order(self, walletId, orderId):
    '''
    cancels an order by order id
    '''
    path = '/wallets/%s/orders/%s' % (walletId, orderId)
    response = self.make_request('DELETE', path, {})
    return response

  def cryptocurrency_withdrawal_request(self, walletId, currency, amount, address):
    '''
    requests a withdrawal to a bitcoin address
    '''
    path = '/wallets/%s/cryptocurrency_withdrawals' % (walletId)
    response = self.make_request('POST', path, {'currency': currency, 'amount': amount, 'address': address})
    return response

  def cryptocurrency_deposit_request(self, walletId, currency):
    '''
    returns a new bitcoin address for deposits to a wallet
    '''
    path = '/wallets/%s/cryptocurrency_deposits' % (walletId)
    response = self.make_request('POST', path, {'currency': currency})
    return response

  def create_wallet_transfer(self, sourceWalletId, destinationWalletId, amount, currencyCode):
    '''
    transfers funds of a single currency between two wallets
    '''
    path = '/wallet_transfers'
    response = self.make_request('POST', path, {'sourceWalletId': sourceWalletId, 'destinationWalletId': destinationWalletId, 'amount': amount, 'currencyCode': currencyCode})
    return response

  def make_request(self, verb, url, body_dict):
    url = ITBIT_BASE_URL + url
    nonce = self._get_next_nonce()
    timestamp = self._get_timestamp()

    if verb in ('PUT', 'POST'):
      json_body = json.dumps(body_dict)
    else:
      json_body = ''

    if self.secret:
      signer = MessageSigner()
      signature = signer.sign_message(self.secret, verb, url, json_body, nonce, timestamp)

      auth_headers = {
        'Authorization': self.clientKey + ':' + signature.decode('utf8'),
        'X-Auth-Timestamp': str(timestamp),
        'X-Auth-Nonce': str(nonce),
        'Content-Type': 'application/json'
      }
    else:
      auth_headers = {
        'X-Auth-Timestamp': str(timestamp),
        'X-Auth-Nonce': str(nonce),
        'Content-Type': 'application/json'
      }

    # TODO: check if request return has a content/header
    return requests.request(verb, url, data=json_body, headers=auth_headers).content

  def _get_next_nonce(self):
    '''
    increases nonce so each request will have a unique nonce
    '''
    self.nonce += 1
    return self.nonce

  def _get_timestamp(self):
    '''
    timestamp must be unix time in milliseconds
    '''
    return int(time.time() * 1000)

  def _generate_query_string(self, filters):
    if filters:
      return '?' + urlparse.urlencode(filters)
    else:
      return ''
