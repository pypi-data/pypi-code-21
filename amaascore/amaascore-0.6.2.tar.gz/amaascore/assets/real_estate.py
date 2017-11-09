from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, date
from dateutil import parser

from amaascore.assets.real_asset import RealAsset


class RealEstate(RealAsset):

    def __init__(self, asset_manager_id, asset_id, asset_issuer_id=None, asset_status='Active',
                 display_name='', description='', country_id=None, venue_id=None, currency=None,
                 ownership=None,
                 comments=None, links=None, references=None, *args, **kwargs):
        super(RealEstate, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                         asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                         display_name=display_name, description=description,
                                         country_id=country_id, venue_id=venue_id,
                                         currency=currency, ownership=ownership,
                                         comments=comments, links=links, references=references,
                                         *args, **kwargs)
