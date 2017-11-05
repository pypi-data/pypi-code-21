import time
import requests
try:
  from urllib import urlencode
  from urlparse import urljoin
except ImportError:
  from urllib.parse import urlencode
  from urllib.parse import urljoin


TUXEXCHANGE_BASE_URL = 'https://tuxexchange.com/api?method={method}' # see https://tuxexchange.com/docs
TUXEXCHANGE_PUBLIC_METHODS = [
  'getticker',
  'get24hvolume',
  'getorders',
  'gettradehistory',
  'getcoins']
TUXEXCHANGE_AUTHENTICATED_METHODS = [
  'getmybalances',
  'withdraw',
  'getmyaddresses',
  'getmytradehistory',
  'buy',
  'sell',
  'getmyopenorders',
  'cancelorder']


def using_requests(request_url):
    return  requests.get(
              request_url
            ).json()


class Tuxexchange(object):
  '''
  Tux Exchange API wrapper
  '''
  def __init__(self, calls_per_second=6, dispatch=using_requests):
    self.dispatch = dispatch
    self.call_rate = 1.0/calls_per_second
    self.last_call = None

  def wait(self):
    if self.last_call is None:
      self.last_call = time.time()
    else:
      now = time.time()
      passed = now - self.last_call
      if passed < self.call_rate:
        #print('sleep')
        time.sleep(1.0 - passed)

      self.last_call = time.time()

  def api_query(self, method, options=None):
    '''
    Queries Tux Exchange with given method and options.

    :param method: Method to query
    :return      : JSON response from Tux Exchange
    :rtype       : dict
    '''
    if not options:
      options = {}
    nonce = str(int(time.time() * 1000))

    request_url = TUXEXCHANGE_BASE_URL.format(method=method)

    request_url += urlencode(options)

    self.wait()

    return self.dispatch(request_url)
