from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal

from amaascore.assets.future import Future
from amaascore.assets.option_mixin import OptionMixin


class FutureOption(Future, OptionMixin):

    def __init__(self, asset_manager_id, asset_id, option_type, option_style, strike, underlying_asset_id,
                 settlement_type, contract_size, point_value, tick_size, quote_unit=None, currency=None,
                 asset_issuer_id=None, asset_status='Active', issue_date=None, expiry_date=None, display_name='',
                 description='', country_id=None, venue_id=None, links=None, references=None, *args, **kwargs):
        self.option_type = option_type
        self.option_style = option_style
        self.strike = strike
        super(FutureOption, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                           asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                           display_name=display_name, currency=currency,
                                           description=description, country_id=country_id, venue_id=venue_id,
                                           links=links, references=references, issue_date=issue_date,
                                           expiry_date=expiry_date, settlement_type=settlement_type,
                                           contract_size=contract_size, point_value=point_value,
                                           tick_size=tick_size, quote_unit=quote_unit,
                                           underlying_asset_id=underlying_asset_id,
                                           *args, **kwargs)
