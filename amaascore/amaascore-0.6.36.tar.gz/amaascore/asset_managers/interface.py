from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.asset_managers.utils import json_to_asset_manager, json_to_relationship,\
                                           json_to_domain
from amaascore.config import ENVIRONMENT
from amaascore.core.interface import Interface


class AssetManagersInterface(Interface):
    """
    The interface to the Asset Managers service for reading Asset Manager information.
    """

    def __init__(self, environment=ENVIRONMENT, logger=None, endpoint=None, username=None, password=None):
        self.logger = logger or logging.getLogger(__name__)
        super(AssetManagersInterface, self).__init__(endpoint=endpoint, endpoint_type='asset_managers',
                                                     environment=environment, username=username, password=password)

    def new(self, asset_manager):
        self.logger.info('New Asset Manager: %s', asset_manager.asset_manager_id)
        url = '%s/asset-managers' % self.endpoint
        response = self.session.post(url, json=asset_manager.to_interface())
        if response.ok:
            asset_manager = json_to_asset_manager(response.json())
            self.logger.info('Successfully Created Asset Manager: %s', asset_manager.asset_manager_id)
            return asset_manager
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id):
        self.logger.info('Retrieve Asset Manager: %s', asset_manager_id)
        url = '%s/asset-managers/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            self.logger.info('Successfully Retrieved Asset Manager: %s', asset_manager_id)
            return json_to_asset_manager(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def deactivate(self, asset_manager_id):
        """
        Is is only possible to deactivate an asset manager if your client_id is also the client_id that was used
        to originally create the asset manager.

        :param asset_manager_id:
        :return:
        """
        self.logger.info('Deactivate Asset Manager: %s', asset_manager_id)
        url = '%s/asset-managers/%s' % (self.endpoint, asset_manager_id)
        response = self.session.delete(url)
        if response.ok:
            self.logger.info('Successfully deactivated Asset Manager: %s', asset_manager_id)
            return json_to_asset_manager(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_ids=None, client_ids=None):
        self.logger.info('Search for Asset Managers: %s', asset_manager_ids)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = ','.join([str(amid) for amid in asset_manager_ids])
        if client_ids:
            search_params['client_ids'] = ','.join(client_ids)
        url = self.endpoint + '/asset-managers'
        response = self.session.get(url, params=search_params)
        if response.ok:
            asset_managers = [json_to_asset_manager(json_asset_manager) for json_asset_manager in response.json()]
            self.logger.info('Returned %s Asset Managers.', len(asset_managers))
            return asset_managers
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def new_relationship(self, relationship):
        self.logger.info('New Asset Manager Relationship: %s and %s', relationship.asset_manager_id,
                         relationship.related_id)
        url = '%s/asset-manager-relationships/%s' % (self.endpoint, relationship.asset_manager_id)
        response = self.session.post(url, json=relationship.to_interface())
        if response.ok:
            self.logger.info('Successfully Created Asset Manager Relationship: %s', relationship.asset_manager_id)
            return json_to_relationship(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend_relationship(self, relationship):
        self.logger.info('Amend Asset Manager Relationship: %s and %s', relationship.asset_manager_id,
                         relationship.related_id)
        url = '%s/asset-manager-relationships/%s' % (self.endpoint, relationship.asset_manager_id)
        response = self.session.put(url, json=relationship.to_interface())
        if response.ok:
            self.logger.info('Successfully Amended Asset Manager Relationship: %s', relationship.asset_manager_id)
            return json_to_relationship(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_relationships(self, asset_manager_id, related_id=None, include_inactive=False):
        self.logger.info('Retrieve Asset Manager Relationship: %s', asset_manager_id)
        url = '%s/asset-manager-relationships/%s' % (self.endpoint, asset_manager_id)
        params = {'include_inactive': include_inactive}
        if related_id:
            params['related_id'] = related_id
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully Retrieved Asset Manager Relationship: %s', asset_manager_id)
            return [json_to_relationship(json_relationship) for json_relationship in response.json()]
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_user_relationships(self, user_asset_manager_id, relationship_types=None, include_inactive=False):
        self.logger.info('Retrieve User Relationships: %s', user_asset_manager_id)
        url = '%s/asset-manager-related-amid/%s' % (self.endpoint, user_asset_manager_id)
        params = {'include_inactive': include_inactive}
        if relationship_types:
            params['relationship_type'] = ','.join(relationship_types)
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully Retrieved User Relationships: %s', user_asset_manager_id)
            return [json_to_relationship(json_relationship) for json_relationship in response.json()]
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def new_domain(self, domain):
        self.logger.info('New Asset Manager Domain: %s for ID %s', domain.domain,
                         domain.asset_manager_id)
        url = '%s/domains/%s' % (self.endpoint, domain.asset_manager_id)
        response = self.session.post(url, json=domain.to_interface())
        if response.ok:
            self.logger.info('Successfully Created Asset Manager Domain for: %s', domain.asset_manager_id)
            return json_to_domain(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def deactivate_domain(self, asset_manager_id, domain):
        self.logger.info('Deactivate Domain: %s for Asset Manager: %s', domain, asset_manager_id)
        url = '%s/domains/%s' % (self.endpoint, asset_manager_id)
        params = {'domain': domain}
        response = self.session.delete(url, params=params)
        if response.ok:
            self.logger.info('Successfully Deactivated Asset Manager Domain: %s', asset_manager_id)
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_domains(self, asset_manager_id, domain_statuses=['Active'], fields=None):
        self.logger.info('Retrieve Asset Manager Domains: %s', asset_manager_id)
        url = '%s/domains/%s' % (self.endpoint, asset_manager_id)
        params = {'domain_statuses': ','.join(domain_statuses)}
        if fields:
            params['fields'] = ','.join(fields)
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully Retrieved Domains: %s', asset_manager_id)
            return [json_to_domain(json_domain) for json_domain in response.json()]
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def check_domains(self, domain):
        self.logger.info('Checking domain: %s', domain)
        url = '%s/domains' % self.endpoint
        params = {'domains': domain}
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully Checked Domain: %s', domain)
            return [json_to_domain(json_domain) for json_domain in response.json()]
        else:
            self.logger.error(response.text)
            response.raise_for_status()
