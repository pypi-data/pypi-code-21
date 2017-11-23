import unittest

from crypto_mediator.clients.helpers import (
    flatten, rename_keys, sort_pair_by_fiat, BittrexClientHelper, LiquiClientHelper, PoloniexClientHelper,
)
from crypto_mediator.fixtures.liqui import ticker as liqui_ticker
from crypto_mediator.fixtures.poloniex import (
    returnCurrencies as poloniex_currencies, returnTicker as poloniex_ticker
)

from crypto_mediator.testing import MockBittrexClient, MockLiquiClient, MockPoloniexClient


class TestUtils(unittest.TestCase):

    def test_flattens_list(self):
        l = [[1, 2], 3, [4, 5, 6, 7]]

        self.assertListEqual(flatten(l), range(1, 8))

    def test_sort_pair_by_fiat(self):
        pair = 'ETH_BTC'
        fiat, currency = sort_pair_by_fiat(pair)

        self.assertEqual(fiat, 'btc')
        self.assertEqual(currency, 'eth')

        FIAT_ORDER = ['best', 'second', 'last']
        pair = 'second_last'
        fiat, currency = sort_pair_by_fiat(pair, fiat_order=FIAT_ORDER)

        self.assertEqual(fiat, 'second')
        self.assertEqual(currency, 'last')

    def test_rename_keys(self):
        data = {
            'price': 1234,
            'sell': 1235,
            'buy': 1233,
        }
        map = {
            'price': 'average_price',
            'sell': 'average_sell',
            'buy': 'average_buy',
        }

        self.assertDictEqual(
            rename_keys(data, map),
            {
                'average_price': 1234,
                'average_sell': 1235,
                'average_buy': 1233,
            }
        )


# TODO: mock clients correctly
class TestBittrexClient(unittest.TestCase):

    def setUp(self):
        BittrexClientHelper.CLIENT_CLASS = MockBittrexClient

        self.credentials = {'api_key': None, 'api_secret': None}
        self.helper = BittrexClientHelper(**self.credentials)

    def test_init(self):
        self.assertIn(('usdt', 'eth'), self.helper.pairs)
        self.assertIn(('btc', 'ltc'), self.helper.pairs)

        self.assertListEqual(self.helper.fiats, ['usdt', 'eth', 'btc'])
        self.assertIn('omg', self.helper.currencies)

    def test_get_pairs(self):
        pairs = self.helper.get_pairs()

        self.assertIn(('usdt', 'eth'), pairs)
        self.assertIn(('btc', 'ltc'), pairs)

    def test_get_currencies(self):
        currencies = self.helper.get_currencies()

        self.assertIn('usdt', currencies)
        self.assertIn('btc', currencies)
        self.assertIn('omg', currencies)

    def test_get_ticker(self):
        ticker_info = self.helper.get_ticker()
        keys = [
            'last',
            'lowest_ask',
            'highest_bid',
            'base_volume',
            'current_volume',
            'high',
            'low',
            'updated',
        ]
        self.assertIn('btc_omg', ticker_info)
        ticker_example = ticker_info['btc_omg']

        self.assertListEqual(sorted(ticker_example.keys()), sorted(keys))


class TestLiquiClient(unittest.TestCase):

    def setUp(self):
        LiquiClientHelper.CLIENT_CLASS = MockLiquiClient

        self.credentials = ['mockKey', 'mockSecret']
        self.helper = LiquiClientHelper(*self.credentials)

    def test_init(self):
        all_currencies = list(set(flatten([p.split('_') for p in liqui_ticker.pairs])))

        self.assertEqual(self.helper.client_pairs, sorted(liqui_ticker.pairs))
        self.assertIn(('usdt', 'eth'), self.helper.pairs)
        self.assertIn(('btc', 'ltc'), self.helper.pairs)

        self.assertListEqual(self.helper.fiats, ['usdt', 'eth', 'btc'])
        self.assertEqual(self.helper.currencies, all_currencies)

    def test_get_pairs(self):
        pairs = self.helper.get_pairs()

        self.assertIn(('usdt', 'eth'), pairs)
        self.assertIn(('btc', 'ltc'), pairs)

    def test_get_currencies(self):
        currencies = self.helper.get_currencies()

        self.assertIn('usdt', currencies)
        self.assertIn('btc', currencies)
        self.assertIn('omg', currencies)

    def test_get_ticker(self):
        ticker_info = self.helper.get_ticker()
        keys = [
            'last',
            'lowest_ask',
            'highest_bid',
            'base_volume',
            'current_volume',
            'high',
            'low',
            'updated',
            'average',
        ]
        self.assertIn('btc_omg', ticker_info)
        ticker_example = ticker_info['btc_omg']

        self.assertListEqual(sorted(ticker_example.keys()), sorted(keys))


class TestPoloniexClient(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        PoloniexClientHelper.CLIENT_CLASS = MockPoloniexClient

        self.credentials = ['mockKey', 'mockSecret']
        self.helper = PoloniexClientHelper(*self.credentials)

        self.client_pairs = poloniex_ticker.response.keys()
        self.currencies = poloniex_currencies.response.keys()

    def test_init(self):
        self.assertIn(('usdt', 'eth'), self.helper.pairs)
        self.assertIn(('btc', 'ltc'), self.helper.pairs)

        self.assertListEqual(self.helper.fiats, ['ltc', 'zec', 'dash', 'xmr', 'btc', 'eth', 'usdt'])
        self.assertIn('ETC', self.helper.currencies)

    def test_get_pairs(self):
        pairs = self.helper.get_pairs()

        self.assertIn(('usdt', 'eth'), pairs)
        self.assertIn(('btc', 'ltc'), pairs)

    def test_get_currencies(self):
        currencies = self.helper.get_currencies()

        self.assertIn('USDT', currencies)
        self.assertIn('BTC', currencies)
        self.assertIn('OMG', currencies)

    def test_get_ticker(self):
        ticker_info = self.helper.get_ticker()
        keys = [
            'id',
            'last',
            'lowest_ask',
            'highest_bid',
            'percent_change',
            'base_volume',
            'quote_volume',
            'is_frozen',
            'high',
            'low',
        ]

        # should exist
        self.assertIn('btc_bcn', ticker_info)
        ticker_example = ticker_info['btc_bcn']
        self.assertListEqual(sorted(ticker_example.keys()), sorted(keys))
