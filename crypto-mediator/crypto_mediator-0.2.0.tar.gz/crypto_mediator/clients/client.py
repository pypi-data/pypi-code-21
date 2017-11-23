import json

from crypto_mediator.clients.helpers import (
    BittrexClientHelper, GDAXClientHelper, LiquiClientHelper, PoloniexClientHelper
)
from crypto_mediator.settings import BITTREX, GDAX, LIQUI, POLONIEX


def downcase(data):
    try:
        return data.lower()
    except:
        return data


class MetaClient(object):
    """
    Interacts with cryptocurrency market clients to,
     - standardize interactions
     - easily interact with multiple clients
     - trade across multiple exchanges

    expects client credentials in the form,
        exchange: {
          key: ...,
          secret: ...,
    """
    HELPER_MAP = {
        BITTREX: BittrexClientHelper,
        GDAX: GDAXClientHelper,
        LIQUI: LiquiClientHelper,
        POLONIEX: PoloniexClientHelper,
    }
    # Actions to take on all individual entries in a response
    DATA_PROCESSORS = [
        downcase,
    ]

    def __init__(self, **exchange_kwargs):
        super(MetaClient, self).__init__()

        self.helpers = {}

        for exchange, kwargs in exchange_kwargs.iteritems():
            HelperClass = self.HELPER_MAP.get(exchange)

            if HelperClass is None:
                raise NotImplementedError('{} is not implemented!'.format(exchange))

            self.helpers[exchange] = HelperClass(**kwargs)

    def _standardize_item(self, item):
        for processor in self.DATA_PROCESSORS:
            item = processor(item)

        return item

    def standardize(self, data):
        datatype = type(data)

        if datatype is list:
            return [self._standardize_item(item) for item in data]
        elif datatype is tuple:
            return (self._standardize_item(item) for item in data)
        elif datatype is dict:
            return {
                self.standardize(key): self.standardize(value)
                for key, value in data.iteritems()
            }

        return self._standardize_item(data)


    def ticker(self, exchange):
        """
        Given an exchange, returns the ticker for all trading pairs
        """
        helper = self.helpers[exchange]
        data = helper.get_ticker()

        return self.standardize(data)

    def pairs(self, exchange):
        """
        Given an exchange, returns all trading pairs
        """
        helper = self.helpers[exchange]
        data = helper.get_pairs()

        return self.standardize(data)
