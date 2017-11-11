from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.parser import parse
from decimal import Decimal
import sys

from amaascore.assets.listed_derivative import ListedDerivative

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Future(ListedDerivative):

    @staticmethod
    def pricing_method():
        return 'Market'

    def __init__(self, asset_manager_id, asset_id, settlement_type, contract_size, point_value, tick_size,
                 underlying_asset_id=None, quote_unit=None, asset_issuer_id=None, asset_status='Active',
                 currency=None, issue_date=date.min, expiry_date=None, display_name='', description='',
                 country_id=None, venue_id=None,
                 links=None, references=None,
                 *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Future'
        self.settlement_type = settlement_type
        self.contract_size = contract_size
        self.point_value = point_value
        self.tick_size = tick_size
        self.quote_unit = quote_unit
        self.underlying_asset_id = underlying_asset_id
        self.expiry_date = expiry_date
        super(Future, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                     asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                     display_name=display_name, currency=currency,
                                     description=description, country_id=country_id, venue_id=venue_id,
                                     links=links, references=references, issue_date=issue_date, expiry_date=expiry_date,
                                     *args, **kwargs)

    @property
    def settlement_type(self):
        return self._settlement_type

    @settlement_type.setter
    def settlement_type(self, settlement_type):
        if settlement_type:
            if settlement_type in ['Physical', 'Cash']:
                self._settlement_type = settlement_type
            else:
                raise ValueError("Invalid value for settlement_type: %s" % settlement_type)

    @property
    def point_value(self):
        return self._point_value

    @point_value.setter
    def point_value(self, point_value):
        """

        :param point_value: This should be replaced with a calculation
        :return:
        """
        if point_value is not None:
            self._point_value = Decimal(point_value)

    @property
    def tick_size(self):
        return self._tick_size

    @tick_size.setter
    def tick_size(self, tick_size):
        """

        :param tick_size:
        :return:
        """
        if tick_size is not None:
            self._tick_size = Decimal(tick_size)

    @property
    def tick_value(self):
        return self.tick_size * self.contract_size

    @property
    def expiry_date(self):
        if hasattr(self, '_expiry_date'):
            return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, value):
        """
        The date on which the Futures contract expires
        :param expiry_date:
        :return:
        """
        if value:
            self._expiry_date = parse(value).date() if isinstance(value, type_check) else value
