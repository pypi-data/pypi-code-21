# coding=utf-8
import unittest

import time
from alas_ce0.management.feature import FeatureClient
from alas_ce0.management.resource import ResourceClient

from config import API_ACCESS_CONFIG


class TestFeatureApi(unittest.TestCase):
    def test_crud(self):
        # Tests Setup

        resource_client = ResourceClient(**API_ACCESS_CONFIG)
        resource = {
            'description': 'TestResource',
            'target': '/target'
        }

        result = resource_client.create(resource)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)
        resource_id = result.content['resource_id']

        # Feature Tests

        feature_client = FeatureClient(**API_ACCESS_CONFIG)
        feature = {
            'name': 'TestFeature',
            'description': 'TestFeatur',
            'resources': [resource_id]
        }

        result = feature_client.create(feature)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = feature_client.get_by_id(result.content['name'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = feature_client.get_by_id('sample-feature')
        self.assertTrue(result.response.status == 404)

        result = feature_client.search({'description': 'TestFeatur'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = feature_client.delete(result.content['items'][0]['name'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = feature_client.create(feature)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        feature['description'] += 'e'
        result = feature_client.update(feature, result.content['name'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = feature_client.delete('TestFeature')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        # Tests Cleanup

        result = resource_client.delete(resource_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
