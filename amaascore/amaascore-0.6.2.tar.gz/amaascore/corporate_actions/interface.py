from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.config import ENVIRONMENT
from amaascore.core.interface import Interface
from amaascore.corporate_actions.utils import json_to_corporate_action


class CorporateActionsInterface(Interface):

    def __init__(self, environment=ENVIRONMENT, logger=None, endpoint=None, username=None, password=None):
        self.logger = logger or logging.getLogger(__name__)
        super(CorporateActionsInterface, self).__init__(endpoint=endpoint, endpoint_type='corporate_actions',
                                                        environment=environment, username=username, password=password)

    def new(self, corporate_action):
        self.logger.info('New Corporate Action - Asset Manager: %s - Corporate Action ID: %s',
                         corporate_action.asset_manager_id, corporate_action.corporate_action_id)
        url = '%s/corporate-actions/%s' % (self.endpoint, corporate_action.asset_manager_id)
        response = self.session.post(url, json=corporate_action.to_interface())
        if response.ok:
            self.logger.info('Successfully Created Corporate Action - Asset Manager: %s - Corporate Action ID: %s',
                             corporate_action.asset_manager_id, corporate_action.corporate_action_id)
            corporate_action = json_to_corporate_action(response.json())
            return corporate_action
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend(self, corporate_action):
        self.logger.info('Amend Corporate Action - Asset Manager: %s - Corporate Action ID: %s',
                         corporate_action.asset_manager_id, corporate_action.corporate_action_id)
        url = '%s/corporate-actions/%s/%s' % (self.endpoint, corporate_action.asset_manager_id,
                                              corporate_action.corporate_action_id)
        response = self.session.put(url, json=corporate_action.to_interface())
        if response.ok:
            self.logger.info('Successfully Amended Corporate Action - Asset Manager: %s - Corporate Action ID: %s',
                             corporate_action.asset_manager_id, corporate_action.corporate_action_id)
            corporate_action = json_to_corporate_action(response.json())
            return corporate_action
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, corporate_action_id, version=None):
        self.logger.info('Retrieve Corporate Action - Asset Manager: %s - Corporate Action ID: %s', asset_manager_id,
                         corporate_action_id)
        url = '%s/corporate-actions/%s/%s' % (self.endpoint, asset_manager_id, corporate_action_id)
        if version:
            url += '?version=%d' % int(version)
        response = self.session.get(url)
        if response.ok:
            self.logger.info('Successfully Retrieved Corporate Action - Asset Manager: %s - Corporate Action ID: %s',
                             asset_manager_id, corporate_action_id)
            return json_to_corporate_action(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def cancel(self, asset_manager_id, corporate_action_id):
        self.logger.info('Cancel Corporate Action - Asset Manager: %s - Corporate Action ID: %s', asset_manager_id,
                         corporate_action_id)
        url = '%s/corporate-actions/%s/%s' % (self.endpoint, asset_manager_id, corporate_action_id)
        json = {'corporate_action_status': 'Cancelled'}
        response = self.session.patch(url, json=json)
        if response.ok:
            self.logger.info('Successfully Cancelled Corporate Action - Asset Manager: %s - Corporate Action ID: %s',
                             asset_manager_id, corporate_action_id)
            return json_to_corporate_action(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_id, corporate_action_ids=None):
        self.logger.info('Search Corporate Actions - Asset Manager: %s', asset_manager_id)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if corporate_action_ids:
            search_params['asset_ids'] = ','.join(corporate_action_ids)
        url = self.endpoint + '/corporate-actions'
        url = '%s/corporate-actions/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url, params=search_params)
        if response.ok:
            corp_actions = [json_to_corporate_action(json_corp_action) for json_corp_action in response.json()]
            self.logger.info('Returned %s Corporate Actions.', len(corp_actions))
            return corp_actions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def corporate_actions_by_asset_manager(self, asset_manager_id):
        self.logger.info('Retrieve Corporate Actions by Asset Manager: %s', asset_manager_id)
        url = '%s/corporate-actions/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            corp_actions = [json_to_corporate_action(json_corp_action) for json_corp_action in response.json()]
            self.logger.info('Returned %s Corporate Actions.', len(corp_actions))
            return corp_actions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def clear(self, asset_manager_id):
        """ This method deletes all the data for an asset_manager_id.
            It should be used with extreme caution.  In production it
            is almost always better to Inactivate rather than delete. """
        self.logger.info('Clear Corporate Actions - Asset Manager: %s', asset_manager_id)
        url = '%s/clear/%s' % (self.endpoint, asset_manager_id)
        response = self.session.delete(url)
        if response.ok:
            count = response.json().get('count', 'Unknown')
            self.logger.info('Deleted %s Corporate Actions.', count)
            return count
        else:
            self.logger.error(response.text)
            response.raise_for_status()
