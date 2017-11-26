from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
from decimal import Decimal

from amaascore.core.amaas_model import AMaaSModel


class Position(AMaaSModel):

    def __init__(self, asset_manager_id, book_id, account_id, accounting_type,
                 asset_id, quantity, average_price=None, client_id=None, *args, **kwargs):
        self.client_id = client_id
        self.asset_manager_id = asset_manager_id
        self.book_id = book_id
        self.account_id = account_id
        self.accounting_type = accounting_type
        self.asset_id = asset_id
        self.quantity = quantity
        self.average_price = average_price
        super(Position, self).__init__(*args, **kwargs)

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        """
        Force the quantity to always be a decimal
        :param value:
        :return:
        """
        self._quantity = Decimal(value)

    @property
    def average_price(self):
        if hasattr(self, '_average_price'):
            return self._average_price

    @average_price.setter
    def average_price(self, value):
        """
        Force the average_price to always be a decimal
        :param value:
        :return:
        """
        if value is not None:
            self._average_price = Decimal(value)