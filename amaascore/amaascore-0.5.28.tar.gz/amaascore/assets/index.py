from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date

from amaascore.assets.asset import Asset


class Index(Asset):

    def __init__(self, asset_id, asset_manager_id, asset_issuer_id=None, asset_status='Active', country_id=None,
                 issue_date=date.min, display_name='', description='', links=None, references=None, *args, **kwargs):
        self.asset_class = 'Index'
        super(Index, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                    asset_issuer_id=asset_issuer_id, asset_status=asset_status, roll_price=False,
                                    display_name=display_name,
                                    country_id=country_id, description=description, links=links, references=references,
                                    issue_date=issue_date, *args, **kwargs)
