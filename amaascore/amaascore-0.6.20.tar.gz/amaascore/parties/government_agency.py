from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.parties.organisation import Organisation


class GovernmentAgency(Organisation):

    def __init__(self, asset_manager_id, party_id, description='', party_status='Active', 
                 display_name='', legal_name='', url='',
                 addresses=None, comments=None, emails=None, links=None, references=None,
                 *args, **kwargs):
        super(GovernmentAgency, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                               description=description, party_status=party_status,
                                               display_name=display_name, legal_name=legal_name, url=url,
                                               addresses=addresses, comments=comments, emails=emails,
                                               links=links, references=references, *args, **kwargs)
