from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.config import ENVIRONMENT
from amaascore.core.interface import Interface
from amaascore.monitor.utils import json_to_item


class MonitorInterface(Interface):

    def __init__(self, environment=ENVIRONMENT, logger=None, endpoint=None, username=None, password=None):
        self.logger = logger or logging.getLogger(__name__)
        super(MonitorInterface, self).__init__(endpoint=endpoint, endpoint_type='monitor', 
                                               environment=environment, username=None, password=None)

    def new_item(self, item):
        url = '%s/items/%s' % (self.endpoint, item.asset_manager_id)
        response = self.session.post(url, json=item.to_interface())
        if response.ok:
            item = json_to_item(response.json())
            return item
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def resubmit_item(self, asset_manager_id, item_id):
        url = '%s/items/%s/%s' % (self.endpoint, asset_manager_id, item_id)
        response = self.session.patch(url)
        if response.ok:
            item = json_to_item(response.json())
            return item
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_item(self, asset_manager_id, item_id):
        url = '%s/items/%s/%s' % (self.endpoint, asset_manager_id, item_id)
        response = self.session.get(url)
        if response.ok:
            return json_to_item(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def close_item(self, asset_manager_id, item_id):
        url = '%s/items/%s/%s' % (self.endpoint, asset_manager_id, item_id)
        response = self.session.delete(url)
        if response.ok:
            self.logger.info('Successfully Closed Item - Asset Manager: %s - Item ID: %s', asset_manager_id, item_id)
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search_items(self, asset_manager_id, item_ids=None):
        self.logger.info('Search Items - Asset Manager: %s', asset_manager_id)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if item_ids:
            search_params['item_ids'] = ','.join(item_ids)
        url = '%s/items/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url, params=search_params)
        if response.ok:
            items = [json_to_item(json_item) for json_item in response.json()]
            self.logger.info('Returned %s Items.', len(items))
            return items
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def items_by_asset_manager(self, asset_manager_id):
        self.logger.info('Retrieve Items by Asset Manager: %s', asset_manager_id)
        url = '%s/items/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            items = [json_to_item(json_item) for json_item in response.json()]
            self.logger.info('Returned %s Items.', len(items))
            return items
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def clear(self, asset_manager_id):
        """ This method deletes all the data for an asset_manager_id.
            It should be used with extreme caution.  In production it
            is almost always better to Close rather than delete. """
        self.logger.info('Clear Monitor - Asset Manager: %s', asset_manager_id)
        url = '%s/clear/%s' % (self.endpoint, asset_manager_id)
        response = self.session.delete(url)
        if response.ok:
            count = response.json().get('count', 'Unknown')
            self.logger.info('Deleted %s Items.', count)
            return count
        else:
            self.logger.error(response.text)
            response.raise_for_status()
