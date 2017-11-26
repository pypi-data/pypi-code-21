from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date

from amaascore.assets.asset import Asset


class Synthetic(Asset):

    def __init__(self, asset_id, asset_manager_id, asset_issuer_id=None, asset_status='Active',
                 country_id=None, currency=None, roll_price=True, display_name='', description='', fungible=True,
                 issue_date=date.min, maturity_date=date.max,
                 comments=None, links=None, references=None, *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Synthetic'
        self.maturity_date = maturity_date
        super(Synthetic, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=fungible,
                                        asset_issuer_id=asset_issuer_id, asset_status=asset_status, currency=currency,
                                        issue_date=issue_date, country_id=country_id,
                                        roll_price=roll_price, display_name=display_name, description=description,
                                        comments=comments, links=links, references=references, *args, **kwargs)
