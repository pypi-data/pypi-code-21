from mock import patch
from unittest import TestCase

from crypto_mediator.clients.client import downcase, MetaClient
from crypto_mediator.testing import MockBittrexClient, MockLiquiClient, MockPoloniexClient


class TestDowncase(TestCase):

    def setUp(self):
        def my_function(str):
            return str

        self.my_function = my_function

    def test_lowercases_data(self):
        my_string = 'aBc 1234 $@!#'
        output = self.my_function(my_string)
        downcased = downcase(output)

        self.assertEqual(downcased, my_string.lower())


# TODO: mock clients correctly
class TestMetaClient(TestCase):

    @patch('liqui.Liqui')
    @patch('poloniex.Poloniex')
    def setUp(self, mockPoloniex, mockLiqui):
        self.maxDiff = None
        self.kwargs = {'liqui': {}, 'poloniex': {}, 'bittrex': {'api_key': None, 'api_secret': None}}
        self.client = MetaClient(**self.kwargs)
        self.client.helpers['bittrex'].client = MockBittrexClient()
        self.client.helpers['liqui'].client = MockLiquiClient()
        self.client.helpers['poloniex'].client = MockPoloniexClient()

    def test_init(self):
        self.assertEqual(len(self.client.helpers), 3)

    def test_init_unsupported_exchange(self):
        self.kwargs['unsupported'] = {}

        with self.assertRaisesRegexp(NotImplementedError, 'unsupported is not implemented!'):
            MetaClient(**self.kwargs)

    def test_bittrex_ticker(self):
        btc_1st = {
            'last': 0.00004692,
            'lowest_ask': 0.00004691,
            'highest_bid': 0.00004633,
            'base_volume': 106.56404429,
            'current_volume': 2241173.71259967,
            'high': 0.00004996,
            'low': 0.00004201,
            'updated': '2017-11-22t20:41:49.297',
        }
        self.assertDictEqual(
            btc_1st,
            self.client.ticker('bittrex')['btc_1st']
        )

    def test_liqui_ticker(self):
        bmc_usdt = {
            'last': 0.6220695,
            'lowest_ask': 0.62508059,
            'highest_bid': 0.61905832,
            'base_volume': 81296.8647402806507957,
            'current_volume': 131309.57718612,
            'high': 0.64828129,
            'low': 0.58545808,
            'updated': 1510788150,
            'average': 0.616869685,
        }
        self.assertDictEqual(
            bmc_usdt,
            self.client.ticker('liqui')['usdt_bmc']
        )

    def test_poloniex_ticker(self):
        btc_bcn = {
            'id': 7,
            'last': '0.00000017',
            'lowest_ask': '0.00000017',
            'highest_bid': '0.00000016',
            'percent_change': '0.00000000',
            'base_volume': '26.85861414',
            'quote_volume': '163214330.95054007',
            'is_frozen': '0',
            'high': '0.00000018',
            'low': '0.00000016',
        }
        data = self.client.ticker('poloniex')
        self.assertDictEqual(
            btc_bcn,
            data['btc_bcn']
        )

    def test_liqui_pairs(self):
        pair = ('btc', 'ltc')
        data = self.client.pairs('liqui')

        self.assertIn(pair, data)

    def test_poloniex_pairs(self):
        pair = ('btc', 'ltc')
        data = self.client.pairs('poloniex')

        self.assertIn(pair, data)