from __future__ import absolute_import, division, print_function, unicode_literals


from amaascore.assets.asset import Asset


class CustomAsset(Asset):

    def __init__(self, asset_manager_id, asset_id, client_additional, maturity_date=None, asset_issuer_id=None,
                 asset_status='Active', roll_price=False, display_name='', description='', country_id=None,
                 currency=None, venue_id=None, issue_date=None, fungible=False,
                 links=None, references=None,
                 *args, **kwargs):
        self.maturity_date = maturity_date
        super(CustomAsset, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=fungible,
                                          asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                          roll_price=roll_price, display_name=display_name, currency=currency,
                                          description=description, country_id=country_id, venue_id=venue_id,
                                          links=links, references=references,
                                          issue_date=issue_date, client_additional=client_additional,
                                          *args, **kwargs)
