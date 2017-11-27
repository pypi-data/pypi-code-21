from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date, datetime
from dateutil import parser
from decimal import Decimal

from amaascore.assets.asset import Asset


class Derivative(Asset):

    def __init__(self, asset_manager_id, asset_id, asset_issuer_id=None,
                 asset_status='Active', display_name='', description='', country_id=None, venue_id=None,
                 issue_date=None, currency=None,
                 comments=None, links=None, references=None,
                 *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Derivative'
        super(Derivative, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=False,
                                         asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                         display_name=display_name, roll_price=False,
                                         description=description, country_id=country_id, venue_id=venue_id,
                                         issue_date=issue_date, currency=currency,
                                         comments=comments, links=links, references=references,
                                         *args, **kwargs)
