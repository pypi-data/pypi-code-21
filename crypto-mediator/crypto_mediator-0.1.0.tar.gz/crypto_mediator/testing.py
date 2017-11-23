from copy import deepcopy
from mock import Mock

from fixtures.bittrex import getmarkets as bittrex_get_markets, getmarketsummaries as bittrex_get_market_summaries
from fixtures.liqui import info as liqui_info, ticker as liqui_ticker
from fixtures.poloniex import (
    returnCurrencies as poloniex_currencies, returnTicker as poloniex_ticker
)


class MockBittrexClient(Mock):

    def get_markets(self):
        return bittrex_get_markets.response

    def get_market_summaries(self):
        return deepcopy(bittrex_get_market_summaries.response)


class MockLiquiClient(Mock):

    def info(self):
        return liqui_info.response

    def ticker(self, pair):
        response = liqui_ticker.response
        pairs = pair.split('-')

        return {p: response[p] for p in pairs}


class MockPoloniexClient(Mock):

    def returnCurrencies(self):
        return poloniex_currencies.response

    def returnTicker(self):
        return poloniex_ticker.response