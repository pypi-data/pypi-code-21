from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, date
from dateutil import parser

from amaascore.assets.derivative import Derivative


class ContractForDifference(Derivative):

    def __init__(self, asset_manager_id, asset_id, asset_issuer_id=None, asset_status='Active', display_name='',
                 description='', country_id=None, venue_id=None, currency=None, issue_date=None,
                 links=None, references=None,
                 *args, **kwargs):
        super(ContractForDifference, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                    asset_issuer_id=asset_issuer_id,
                                                    asset_status=asset_status, display_name=display_name,
                                                    description=description,
                                                    country_id=country_id, venue_id=venue_id, issue_date=issue_date,
                                                    currency=currency, links=links,
                                                    references=references,
                                                    *args, **kwargs)
