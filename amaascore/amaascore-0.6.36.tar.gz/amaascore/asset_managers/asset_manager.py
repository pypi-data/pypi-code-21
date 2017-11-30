from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import timedelta
from dateutil.parser import parse

from amaascore.asset_managers.enums import ACCOUNT_TYPES, ASSET_MANAGER_TYPES
from amaascore.core.amaas_model import AMaaSModel
from amaascore.error_messages import ERROR_LOOKUP


class AssetManager(AMaaSModel):

    def __init__(self, asset_manager_type, asset_manager_id=None, asset_manager_status='Active', party_id=None,
                 account_type='Basic', default_book_owner_id='', default_timezone='UTC',
                 default_book_close_time=timedelta(hours=18), language_code='en-US',
                 *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.asset_manager_type = asset_manager_type
        self.asset_manager_status = asset_manager_status
        self.party_id = party_id
        self.default_book_owner_id = default_book_owner_id
        self.default_timezone = default_timezone
        self.default_book_close_time = default_book_close_time
        self.account_type = account_type
        self.language_code = language_code
        super(AssetManager, self).__init__(*args, **kwargs)

    @property
    def asset_manager_type(self):
        return self._asset_manager_type

    @asset_manager_type.setter
    def asset_manager_type(self, asset_manager_type):
        if asset_manager_type:
            if asset_manager_type in ASSET_MANAGER_TYPES:
                self._asset_manager_type = asset_manager_type
            else:
                raise ValueError(ERROR_LOOKUP.get('am_type_invalid') % (asset_manager_type,
                                                                        self.asset_manager_id))

    @property
    def account_type(self):
        if hasattr(self, '_account_type'):
            return self._account_type

    @account_type.setter
    def account_type(self, account_type):
        if account_type:
            if account_type in ACCOUNT_TYPES:
                self._account_type = account_type
            else:
                raise ValueError(ERROR_LOOKUP.get('am_account_type_invalid') % (account_type,
                                                                                self.asset_manager_id))
