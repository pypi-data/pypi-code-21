from crypto_exchange_apis import itBit
from crypto_exchange_apis import Bitfinex
from crypto_exchange_apis import Bitstamp
from crypto_exchange_apis import GDAX
from crypto_exchange_apis import Bittrex
from crypto_exchange_apis import Poloniex
from crypto_exchange_apis import Tuxexchange

import unittest
import os.path


def test_basic_itbit_response(unit_test, result):
  if 'code' in result:
    unit_test.assertTrue(result['code'] is 80012, '404')
  if 'description' in result:
    unit_test.assertTrue('no market' in str(result['description']).lower(), 'Invalid market ticker')
    unit_test.assertTrue(result['code'] is 80012, '404')

def test_basic_bitfinex_response(unit_test, result):
  if 'message' in result:
    unit_test.assertTrue('unknown symbol' in str(result['message']).lower(), 'Unknown ticker symbol')

def test_basic_bitstamp_response(unit_test, result, method_name):
  if method_name == 'ticker':
    unit_test.assertTrue('high' in str(result).lower(), 'Unrecognized result format')
  if method_name == 'order_book':
    unit_test.assertTrue('bids' in str(result).lower(), 'Unrecognized result format')

def test_basic_bittrex_response(unit_test, result, method_name):
  unit_test.assertTrue(result['success'], '{0:s} failed'.format(method_name))
  unit_test.assertTrue(result['message'] is not None, 'message not present in response')
  unit_test.assertTrue(result['result'] is not None, 'result not present in response')

def test_basic_gdax_response(unit_test, result):
  if 'message' in result:
    unit_test.assertTrue('notfound' in str(result['message']).lower(), 'Unrecognized ticker symbol')

def test_basic_poloniex_response(unit_test, result):
  if 'error' in result:
    unit_test.assertTrue(result['error'] is None, 'error is present in response')

def test_basic_tuxexchange_response(unit_test, result):
  if 'success' in result:
    unit_test.assertTrue(result['success'] is 0, 'success is 0')
  if 'error' in result:
    unit_test.assertTrue(result['error'] is None, 'error is present in response')


def test_authenticated_bittrex_reponse(unit_test, result, test_type):
  unit_test.assertFalse(result['success'], '{0:s} failed'.format(test_type))
  unit_test.assertTrue('invalid' in str(result['message']).lower(), '{0:s} failed response message'.format(test_type))
  unit_test.assertIsNone(result['result'], '{0:s} failed response result not None'.format(test_type))


class TestitBitPublicAPI(unittest.TestCase):
  '''
  Integration tests for the itBit public API.
  These will fail in the absence of an internet connection or if the Poloniex API goes down
  '''
  def setUp(self):
    self.itbit = itBit()

  def test_get_ticker(self):
    actual = self.itbit.get_ticker()
    test_basic_itbit_response(self, actual)
    pass

  def test_get_coins(self):
    actual = self.itbit.get_order_book()
    test_basic_itbit_response(self, actual)
    pass

class TestBittrexPublicAPI(unittest.TestCase):
  '''
  Integration tests for the Bittrex public API.
  These will fail in the absence of an internet connection or if bittrex API goes down
  '''
  def setUp(self):
    self.bittrex = Bittrex(None, None)

  def test_handles_none_key_or_secret(self):
    self.bittrex = Bittrex(None, None)
    # could call any public method here
    actual = self.bittrex.get_markets()
    self.assertTrue(actual['success'], 'failed with None key and None secret')

    self.bittrex = Bittrex('123', None)
    actual = self.bittrex.get_markets()
    self.assertTrue(actual['success'], 'failed with None secret')

    self.bittrex = Bittrex(None, '123')
    self.assertTrue(actual['success'], 'failed with None key')
    pass

  def test_get_markets(self):
    actual = self.bittrex.get_markets()
    test_basic_bittrex_response(self, actual, 'get_markets')
    self.assertTrue(isinstance(actual['result'], list), 'result is not a list')
    self.assertTrue(len(actual['result']) > 0, 'result list is 0-length')
    pass

  def test_get_currencies(self):
    actual = self.bittrex.get_currencies()
    test_basic_bittrex_response(self, actual, 'get_currencies')
    pass

class TestBitstampPublicAPI(unittest.TestCase):
  '''
  Integration tests for the Bitstamp public API.
  These will fail in the absence of an internet connection or if the Poloniex API goes down
  '''
  def setUp(self):
    self.bitstamp = Bitstamp()

  def test_get_ticker(self):
    actual = self.bitstamp.ticker()
    test_basic_bitstamp_response(self, actual, 'ticker')
    pass

  def test_get_order_book(self):
    actual = self.bitstamp.order_book()
    test_basic_bitstamp_response(self, actual, 'corder_book')
    pass

class TestGDAXPublicAPI(unittest.TestCase):
  '''
  Integration tests for the GDAX public API.
  These will fail in the absence of an internet connection or if the GDAX API goes down
  '''
  def setUp(self):
    self.gdax = GDAX()

  def test_basic_gdax_response(self):
    actual = self.gdax.get_product_ticker()
    test_basic_gdax_response(self, actual)
    pass

  def test_basic_gdax_response(self):
    actual = self.gdax.get_product_order_book()
    test_basic_gdax_response(self, actual)
    pass

class TestPoloniexPublicAPI(unittest.TestCase):
  '''
  Integration tests for the Poloniex public API.
  These will fail in the absence of an internet connection or if the Poloniex API goes down
  '''
  def setUp(self):
    self.poloniex = Poloniex()

  def test_get_ticker(self):
    actual = self.poloniex.returnTicker()
    test_basic_poloniex_response(self, actual)
    pass

  def test_get_coins(self):
    actual = self.poloniex.returnCurrencies()
    test_basic_poloniex_response(self, actual)
    pass

class TestTuxExchangePublicAPI(unittest.TestCase):
  '''
  Integration tests for the Tux Exchange public API.
  These will fail in the absence of an internet connection or if the Tux Exchange API goes down
  '''
  def setUp(self):
    self.tuxexchange = Tuxexchange()

  def test_get_ticker(self):
    actual = self.tuxexchange.api_query('getticker')
    test_basic_tuxexchange_response(self, actual)
    pass

  def test_get_coins(self):
    actual = self.tuxexchange.api_query('getcoins')
    test_basic_tuxexchange_response(self, actual)
    pass


class TestBittrexAuthenticatedAPI(unittest.TestCase):
  '''
  Integration tests for the authenticated Bittrex  API.
    * These will fail in the absence of an internet connection or if bittrex API goes down.
    * They require a valid API key and secret issued by Bittrex.
    * They also require the presence of a JSON file called 'auth.json'.
    It is structured as such:
  {
    'bittrex': {
      'key': '12341253456345',
      'secret': '3345745634234534'
    }
  }
  '''
  def setUp(self):
    if os.path.isfile('auth.json'):
      with open('auth.json') as secrets_file:
        self.secrets = json.load(secrets_file)
        secrets_file.close()
      if 'bittrex' in self.secrets:
        self.bittrex = Bittrex(self.secrets['bittrex']['key'], self.secrets['bittrex']['secret'])
      else:
        self.noauth = True
    else:
      self.noauth = True

  def test_handles_invalid_key_or_secret(self):
    if not self.noauth:
      self.bittrex = Bittrex('invalidkey', self.secrets['secret'])
      actual = self.bittrex.get_balance('BTC')
      test_authenticated_bittrex_reponse(self, actual, 'Invalid key, valid secret')

      self.bittrex = Bittrex(None, self.secrets['secret'])
      actual = self.bittrex.get_balance('BTC')
      test_authenticated_bittrex_reponse(self, actual, 'None key, valid secret')

      self.bittrex = Bittrex(self.secrets['key'], 'invalidsecret')
      actual = self.bittrex.get_balance('BTC')
      test_authenticated_bittrex_reponse(self, actual, 'valid key, invalid secret')

      self.bittrex = Bittrex(self.secrets['key'], None)
      actual = self.bittrex.get_balance('BTC')
      test_authenticated_bittrex_reponse(self, actual, 'valid key, None secret')

      self.bittrex = Bittrex('invalidkey', 'invalidsecret')
      actual = self.bittrex.get_balance('BTC')
      test_authenticated_bittrex_reponse(self, actual, 'invalid key, invalid secret')
    pass

  def test_get_balance(self):
    if not self.noauth:
      actual = self.bittrex.get_balance('BTC')
      test_basic_bittrex_response(self, actual, 'getbalance')
      self.assertTrue(isinstance(actual['result'], dict), 'result is not a dict')
      self.assertEqual(actual['result']['Currency'],
                       'BTC',
                       'requested currency {0:s} does not match returned currency {1:s}'
                       .format('BTC', actual['result']['Currency']))
      pass


if __name__ == '__main__':
  unittest.main()
