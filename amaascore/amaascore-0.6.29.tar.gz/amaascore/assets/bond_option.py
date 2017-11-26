from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date, datetime
from dateutil.parser import parse
import sys

from amaascore.assets.derivative import Derivative
from amaascore.assets.option_mixin import OptionMixin

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class BondOption(Derivative, OptionMixin):

    def __init__(self, asset_manager_id, option_type, strike, underlying_asset_id, option_style, asset_id=None,
                 asset_issuer_id=None, asset_status='Active', display_name='', description='', country_id=None,
                 currency=None, venue_id=None, issue_date=date.min, expiry_date=date.max,
                 links=None, references=None, *args, **kwargs):
        self.option_type = option_type
        self.strike = strike
        self.underlying_asset_id = underlying_asset_id
        self.option_style = option_style
        self.expiry_date = expiry_date
        super(BondOption, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                         asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                         display_name=display_name, currency=currency,
                                         description=description, country_id=country_id, venue_id=venue_id,
                                         links=links, references=references,
                                         issue_date=issue_date, *args, **kwargs)

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
