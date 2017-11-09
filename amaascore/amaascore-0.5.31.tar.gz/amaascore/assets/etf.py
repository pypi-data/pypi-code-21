from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, date
from dateutil import parser

from amaascore.assets.fund import Fund


class ExchangeTradedFund(Fund):

    @staticmethod
    def pricing_method():  # Only ETF is market priced, other funds default to derived type (most likely user manually key in price)
        return 'Market'   

    def __init__(self, asset_manager_id, asset_id, nav=None, expense_ratio=None, net_assets=None,
                 asset_issuer_id=None, asset_status='Active', description='', display_name='', roll_price=False,
                 country_id=None, venue_id=None, currency=None, creation_date=None,
                 links=None, references=None,
                 *args, **kwargs):
        super(ExchangeTradedFund, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                 asset_issuer_id=asset_issuer_id,
                                                 asset_status=asset_status, roll_price=roll_price,
                                                 display_name=display_name, description=description,
                                                 country_id=country_id, venue_id=venue_id,
                                                 creation_date=creation_date, fund_type='ETF',
                                                 net_assets=net_assets, nav=nav, expense_ratio=expense_ratio,
                                                 currency=currency, links=links, references=references,
                                                 *args, **kwargs)
