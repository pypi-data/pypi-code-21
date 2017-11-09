from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.parties.company import Company


class Broker(Company):

    def __init__(self, asset_manager_id, party_id, base_currency=None, display_name='', legal_name='', url='',  description='', party_status='Active',
                 addresses=None, emails=None, links=None, references=None,
                 *args, **kwargs):
        super(Broker, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id, base_currency=base_currency,
                                     description=description, party_status=party_status,
                                     display_name=display_name, legal_name=legal_name, url=url, 
                                     addresses=addresses, emails=emails, links=links,
                                     references=references, *args, **kwargs)

# TODO - Add markets covered, products covered
