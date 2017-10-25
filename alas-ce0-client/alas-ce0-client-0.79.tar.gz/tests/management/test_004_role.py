# coding=utf-8
import time
import unittest

from alas_ce0.management.feature import FeatureClient

from alas_ce0.management.resource import ResourceClient

from alas_ce0.management.role import RoleClient
from config import API_ACCESS_CONFIG


class TestRoleApi(unittest.TestCase):
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

        feature_client = FeatureClient(**API_ACCESS_CONFIG)
        feature = {
            'name': 'TestFeature',
            'description': 'TestFeature',
            'resources': [resource_id]
        }

        result = feature_client.create(feature)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        # Role Tests

        role_client = RoleClient(**API_ACCESS_CONFIG)
        role = {
            'name': 'TestRole',
            'description': 'TestRol',
            'features': ["TestFeature"]
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

        result = role_client.delete('TestRole')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        # Tests Cleanup

        result = feature_client.delete('TestFeature')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = resource_client.delete(resource_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
