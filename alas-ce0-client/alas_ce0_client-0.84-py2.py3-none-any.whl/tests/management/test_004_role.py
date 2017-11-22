# coding=utf-8
import unittest

import time
from sdp_dtv.management.feature import FeatureClient
from sdp_dtv.management.role import RoleClient
from tests import API_ACCESS_CONFIG


class TestRoleApi(unittest.TestCase):
    def test_crud(self):
        feature_client = FeatureClient(**API_ACCESS_CONFIG)

        result = feature_client.search({'description': 'TestFeature'})
        self.assertTrue(result.response.status == 200 and result.content)

        role_client = RoleClient(**API_ACCESS_CONFIG)
        role = {
            'name': 'TestRole',
            'description': 'TestRol',
            'features': [result.content['items'][0]['name']]
        }

        result = role_client.create(role)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = role_client.get_by_id(result.content['name'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = role_client.get_by_id('sample-role')
        self.assertTrue(result.response.status == 404)

        result = role_client.search({'description': 'TestRol'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = role_client.delete(result.content['items'][0]['name'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = role_client.create(role)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        role['description'] += 'e'
        result = role_client.update(role, result.content['name'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
