from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date, datetime
from dateutil import parser
from decimal import Decimal

from amaascore.assets.asset import Asset


class ListedDerivative(Asset):

    def __init__(self, asset_manager_id, asset_id, asset_issuer_id=None, asset_status='Active', currency=None,
                 display_name='', description='', country_id=None, venue_id=None, issue_date=date.min,
                 links=None, references=None,
                 *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'ListedDerivative'

        super(ListedDerivative, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                               asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                               roll_price=False, display_name=display_name, currency=currency,
                                               description=description, country_id=country_id, venue_id=venue_id,
                                               issue_date=issue_date, links=links, references=references,
                                               *args, **kwargs)
