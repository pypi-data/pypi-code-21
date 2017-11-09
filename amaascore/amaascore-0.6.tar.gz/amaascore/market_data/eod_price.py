from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.parser import parse
from decimal import Decimal
import sys

from amaascore.core.amaas_model import AMaaSModel

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class EODPrice(AMaaSModel):

    def __init__(self, asset_manager_id, asset_id, business_date, price, active=True, *args, **kwargs):
        """

        :param asset_manager_id: The asset_manager_id who owns this price
        :param asset_id:  The asset_id for which we are providing a price
        :param business_date:  The business date for which this is the EOD price
        :param price: The price itself
        :param active: A boolean indicator of whether this price can be used or whether it has been deactivated
        """
        self.asset_manager_id = asset_manager_id
        self.asset_id = asset_id
        self.price = price
        self.business_date = business_date
        self.active = active
        super(EODPrice, self).__init__(*args, **kwargs)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        """
        Force the price to always be a decimal
        :param value:
        :return:
        """
        if value is not None:
            self._price = Decimal(value)

    @property
    def business_date(self):
        return self._business_date

    @business_date.setter
    def business_date(self, business_date):
        """
        Force the business_date to always be a date
        :param business_date:
        :return:
        """
        if business_date is not None:
            if isinstance(business_date, type_check):
                self._business_date = parse(business_date).date()
            else:
                self._business_date = business_date
