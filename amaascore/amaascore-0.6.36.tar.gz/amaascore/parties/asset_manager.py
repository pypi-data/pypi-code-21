from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.parties.company import Company


class AssetManager(Company):
    """
    This represents a Company engaged in Asset Management activity.
    """

    def __init__(self, asset_manager_id, party_id, base_currency=None, display_name='',
                 legal_name='', url='', description='', party_status='Active',
                 year_of_incorporation=None, contact_number=None, license_type=None,
                 license_number=None, assets_under_management=None, registration_number=None,
                 addresses=None, emails=None, links=None, references=None,
                 *args, **kwargs):
        self.license_type = license_type
        self.license_number = license_number
        self.assets_under_management = assets_under_management
        self.registration_number = registration_number
        super(AssetManager, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                           base_currency=base_currency, display_name=display_name,
                                           legal_name=legal_name, url=url,
                                           description=description, party_status=party_status,
                                           year_of_incorporation=year_of_incorporation,
                                           contact_number=contact_number,
                                           addresses=addresses, emails=emails,
                                           links=links, references=references, *args, **kwargs)
