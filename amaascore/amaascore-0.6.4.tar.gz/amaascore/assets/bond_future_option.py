from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from decimal import Decimal

from amaascore.assets.future_option import FutureOption


class BondFutureOption(FutureOption):

    def __init__(self, asset_manager_id, asset_id, option_type, option_style, strike, underlying_asset_id,
                 settlement_type, contract_size, point_value, tick_size, quote_unit=None, currency=None,
                 asset_issuer_id=None, asset_status='Active', issue_date=date.min, expiry_date=date.max,
                 display_name='', description='', country_id=None, venue_id=None,
                 links=None, references=None, *args, **kwargs):
        """

        :param asset_manager_id: The asset manager who owns the data for this BondFutureOption
        :param asset_id: The owning asset manager's unique identifier for this BondFutureOption
        :param option_type: Whether this is a put option or a call option
        :param option_style: The style of the option - e.g. American, European
        :param strike: The option strike price
        :param underlying_asset_id: The owning asset manager's identifier for the asset which underlies this option
        :param asset_issuer_id: The owning asset manager's identifier for the issuer of this option
        :param asset_status: The status of this BondFutureOption
        :param issue_date: The date on which this BondFutureOption was created
        :param expiry_date: The date on which this BondFutureOption will expire
        :param display_name: A human-readable name for this BondFutureOption
        :param description: A human-readable description of this BondFutureOption
        :param country_id: The ISO 3166-1 alpha-3 code for the country that this BondFutureOption was issued in
        :param venue_id: The ISO-10383 identifier for the venue on which this BondFutureOption trades
        :param links: Links to other relevant assets
        :param references: A dictionary of additional References for this BondFutureOption
        :param args:
        :param kwargs:
        """
        super(BondFutureOption, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                               asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                               display_name=display_name, currency=currency,
                                               description=description, country_id=country_id, venue_id=venue_id,
                                               links=links, references=references, issue_date=issue_date,
                                               expiry_date=expiry_date, option_style=option_style, strike=strike,
                                               option_type=option_type, settlement_type=settlement_type,
                                               contract_size=contract_size, point_value=point_value,
                                               tick_size=tick_size, quote_unit=quote_unit,
                                               underlying_asset_id=underlying_asset_id,
                                               *args, **kwargs)
