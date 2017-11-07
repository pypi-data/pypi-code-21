from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
from dateutil.parser import parse
from decimal import Decimal
import sys

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Quote(object):

    def __init__(self, asset_manager_id, asset_id, quote_datetime, bid=None, ask=None):
        self.asset_manager_id = asset_manager_id
        self.asset_id = asset_id
        self.quote_datetime = quote_datetime
        self.bid = bid
        self.ask = ask

    @property
    def quote_datetime(self):
        return self._quote_datetime

    @quote_datetime.setter
    def quote_datetime(self, value):
        """
        Force the quote_datetime to always be a datetime
        :param value:
        :return:
        """
        if value:
            if isinstance(value, type_check):
                self._quote_datetime = parse(value)
            elif isinstance(value, datetime.datetime):
                self._quote_datetime = value

    @property
    def bid(self):
        return self._bid

    @bid.setter
    def bid(self, value):
        """
        Force the bid to always be a decimal
        :param value:
        :return:
        """
        if value is not None:
            self._bid = Decimal(value)

    @property
    def ask(self):
        return self._ask

    @ask.setter
    def ask(self, value):
        """
        Force the ask to always be a decimal
        :param value:
        :return:
        """
        if value is not None:
            self._ask = Decimal(value)

    def mid(self):
        return (self.bid + self.ask) / 2