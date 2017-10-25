# coding=utf-8
import unittest

import time
from sdp_dtv.management.feature import FeatureClient
from sdp_dtv.management.resource import ResourceClient
from tests import API_ACCESS_CONFIG


class TestFeatureApi(unittest.TestCase):
    def test_crud(self):
        resource_client = ResourceClient(**API_ACCESS_CONFIG)
        result = resource_client.search({'target': '/target'})
        self.assertTrue(result.response.status == 200 and result.content)

        feature_client = FeatureClient(**API_ACCESS_CONFIG)
        feature = {
            'name': 'TestFeature',
            'description': 'TestFeatur',
            'resources': [result.content['items'][0]['resource_id']]
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


if __name__ == '__main__':
    unittest.main()