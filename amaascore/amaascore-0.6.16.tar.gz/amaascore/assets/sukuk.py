from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.assets.asset import Asset


class Sukuk(Asset):

    def __init__(self, asset_manager_id, asset_id, maturity_date, asset_issuer_id=None,
                 asset_status='Active', roll_price=True, issue_date=None, display_name='', description='',
                 country_id=None, venue_id=None, currency=None,
                 comments=None, links=None, references=None, *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Sukuk'
        self.maturity_date = maturity_date
        super(Sukuk, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                    asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                    roll_price=roll_price, display_name=display_name, currency=currency,
                                    description=description, country_id=country_id, venue_id=venue_id,
                                    comments=comments, links=links, references=references,
                                    issue_date=issue_date,
                                    *args, **kwargs)
