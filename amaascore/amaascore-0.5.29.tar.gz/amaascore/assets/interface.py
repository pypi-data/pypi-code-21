from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging

from amaascore.assets.utils import json_to_asset
from amaascore.config import ENVIRONMENT
from amaascore.core.interface import Interface
from amaascore.core.amaas_model import json_handler


class AssetsInterface(Interface):

    def __init__(self, environment=ENVIRONMENT, endpoint=None, logger=None, username=None, password=None):
        self.logger = logger or logging.getLogger(__name__)
        super(AssetsInterface, self).__init__(endpoint=endpoint, endpoint_type='assets',
                                              environment=environment, username=username, password=password)

    def new(self, asset):
        self.logger.info('New Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id, asset.asset_id)
        url = '%s/assets/%s' % (self.endpoint, asset.asset_manager_id)
        response = self.session.post(url, json=asset.to_interface())
        if response.ok:
            self.logger.info('Successfully Created Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id,
                             asset.asset_id)
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def create_many(self, assets):
        if not assets or not isinstance(assets, list):
            raise ValueError('Invalid argument. Argument must be a non-empty list.')

        self.logger.info('New Assets - Asset Manager: %s', assets[0].asset_manager_id)
        url = '%s/assets/%s' % (self.endpoint, assets[0].asset_manager_id)
        json_body = [asset.to_interface() for asset in assets]
        response = self.session.post(url, json=json_body)
        if response.ok:
            self.logger.info('Successfully Created Assets - Asset Manager: %s', assets[0].asset_manager_id)
            assets = [asset for asset in response.json()]
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def upsert(self, asset):
        ''' upsert only support upserting one asset at a time'''
        self.logger.info('Upsert Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id, asset.asset_id)
        url = '%s/assets/%s' % (self.endpoint, asset.asset_manager_id)
        response = self.session.post(url, json=asset.to_interface(), params={'upsert': True})
        if response.ok:
            self.logger.info('Successfully Upserted Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id,
                             asset.asset_id)
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()


    def amend(self, asset):
        self.logger.info('Amend Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id, asset.asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset.asset_manager_id, asset.asset_id)
        response = self.session.put(url, json=asset.to_interface())
        if response.ok:
            self.logger.info('Successfully Amended Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id,
                             asset.asset_id)
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def partial(self, asset_manager_id, asset_id, updates):
        self.logger.info('Partial Amend Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id,
                         asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        # Setting handler ourselves so we can be sure Decimals work
        response = self.session.patch(url, data=json.dumps(updates, default=json_handler), headers=self.json_header)
        if response.ok:
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, asset_id, version=None):
        self.logger.info('Retrieve Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id, asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        if version:
            url += '?version=%d' % int(version)
        response = self.session.get(url)
        if response.ok:
            self.logger.info('Successfully Retrieved Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id,
                             asset_id)
            return json_to_asset(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def deactivate(self, asset_manager_id, asset_id):
        self.logger.info('Deactivate Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id, asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        json = {'asset_status': 'Inactive'}
        response = self.session.patch(url, json=json)
        if response.ok:
            self.logger.info('Successfully Deactivated Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id,
                             asset_id)
            return json_to_asset(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_id, asset_ids=None, asset_classes=None, asset_types=None,
               page_no=None, page_size=None):
        self.logger.info('Search for Assets - Asset Manager: %s', asset_manager_id)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_ids:
            search_params['asset_ids'] = ','.join(asset_ids)
        if asset_classes:
            search_params['asset_classes'] = ','.join(asset_classes)
        if asset_types:
            search_params['asset_types'] = ','.join(asset_types)
        if page_no is not None:
            search_params['page_no'] = page_no
        if page_size:
            search_params['page_size'] = page_size
        url = '%s/assets/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url, params=search_params)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            self.logger.info('Returned %s Assets.', len(assets))
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def fields_search(self, asset_manager_ids=None, asset_ids=None, asset_classes=None, asset_types=None,
                      fields=None, page_no=None, page_size=None):
        self.logger.info('Search for Assets - Asset Manager(s): %s', asset_manager_ids)
        search_params = {}

        if asset_manager_ids:
            search_params['asset_manager_ids'] = ','.join([str(amid) for amid in asset_manager_ids])
        if asset_ids:
            search_params['asset_ids'] = ','.join(asset_ids)
        if asset_classes:
            search_params['asset_classes'] = ','.join(asset_classes)
        if asset_types:
            search_params['asset_types'] = ','.join(asset_types)
        if fields:
            search_params['fields'] = ','.join(fields)
        if page_no is not None:
            search_params['page_no'] = page_no
        if page_size:
            search_params['page_size'] = page_size

        url = self.endpoint + '/assets'
        response = self.session.get(url, params=search_params)
        if response.ok:
            asset_dicts = response.json()
            self.logger.info('Returned %s Assets.', len(asset_dicts))
            return asset_dicts
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def assets_by_asset_manager(self, asset_manager_id):
        self.logger.info('Retrieve Assets By Asset Manager: %s', asset_manager_id)
        url = '%s/assets/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            self.logger.info('Returned %s Assets.', len(assets))
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def clear(self, asset_manager_id):
        """ This method deletes all the data for an asset_manager_id.
            It should be used with extreme caution.  In production it
            is almost always better to Inactivate rather than delete. """
        self.logger.info('Clear Assets - Asset Manager: %s', asset_manager_id)
        url = '%s/clear/%s' % (self.endpoint, asset_manager_id)
        response = self.session.delete(url)
        if response.ok:
            count = response.json().get('count', 'Unknown')
            self.logger.info('Deleted %s Assets.', count)
            return count
        else:
            self.logger.error(response.text)
            response.raise_for_status()
