from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.parties.organisation import Organisation


class Company(Organisation):
    """
    Represents a legal entity that has incorporated in a jurisdiction.  Does not specifiy
    anything about the structure of the company (e.g. Public, Private Limited, Partnership, etc)
    """

    def __init__(self, asset_manager_id, party_id, base_currency=None, display_name='',
                 legal_name='', url='', description='', party_status='Active',
                 year_of_incorporation=None, contact_number=None,
                 addresses=None, comments=None, emails=None, links=None, references=None,
                 *args, **kwargs):
        if not hasattr(self, 'party_class'):  # More specific child class may have already set this
            self.party_class = 'Company'
        self.year_of_incorporation = year_of_incorporation
        self.contact_number = contact_number
        super(Company, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                      base_currency=base_currency, description=description,
                                      party_status=party_status, display_name=display_name,
                                      legal_name=legal_name, url=url,
                                      addresses=addresses, comments=comments, emails=emails,
                                      links=links, references=references,
                                      *args, **kwargs)
