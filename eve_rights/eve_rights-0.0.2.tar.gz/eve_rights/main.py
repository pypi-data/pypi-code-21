# -*- coding: utf-8 -*-

from .config import set_config_fields
from .hooks import (get_restricted_resources,
                    on_update,
                    init_document_with_acl,
                    on_delete,
                    on_list)
from eve.io.mongo import Mongo, Validator, GridFSMediaStorage, create_index
from eve import Eve as _Eve


class Eve(_Eve):

    """ Eve application overriding """

    def register_rights(self, account_resource="accounts", acl_fields_prefix="w_", resource_blacklist=[]):

        """ Alterate the config to handle per-item rights

                >>> app = Eve()
                >>> app.register_rights(account_resource="people")
                >>> # Ok

            :param account_resource The accounts resource name, it can be something like: 'user, users, account, people'
            :param acl_fields_prefix
            :param resource_blacklist
        """

        self.config['ACCOUNT_RESOURCE'] = account_resource
        self.config['RESOURCE_BLACKLIST'] = resource_blacklist
        self.config['ACL_FIELDS_READ'] = acl_fields_prefix + "read"
        self.config['ACL_FIELDS_WRITE'] = acl_fields_prefix + "write"
        self.config['RESTRICTED_RESOURCES'] = get_restricted_resources(self)
        # Add the rights fields in the schema definition
        self.set_config_fields()

    def register_hooks(self):

        """ Register the hook functions to the eve app to call after construction """

        self.on_pre_GET += on_list
        self.on_delete_item += on_delete
        self.on_insert += init_document_with_acl
        self.on_update += on_update

    def set_config_fields(self):

        """  Add custom who can read/right fields in the schema so we can know the documents rights

            :param app the eve application
        """

        account_definition = {
            'type': 'list',
            'default': [],
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': self.config['ACCOUNT_RESOURCE'],
                    'field': '_id',
                },
            }
        }
        for resource in self.config['DOMAIN']:
            if resource != self.config['ACCOUNT_RESOURCE'] and resource not in self.config['RESOURCE_BLACKLIST']:
                self.config['DOMAIN'][resource]['schema'][self.config['ACL_FIELDS_READ']] = account_definition
                self.config['DOMAIN'][resource]['schema'][self.config['ACL_FIELDS_WRITE']] = account_definition
