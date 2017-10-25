# coding=utf-8
import time
import unittest

from alas_ce0.management.role import RoleClient

from alas_ce0.management.feature import FeatureClient

from alas_ce0.management.resource import ResourceClient

from alas_ce0.management.roles_group import RolesGroupClient
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

        role_client = RoleClient(**API_ACCESS_CONFIG)
        role = {
            'name': 'TestRole',
            'description': 'TestRole',
            'features': ["TestFeature"]
        }

        result = role_client.create(role)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        # RolesGroup Tests

        roles_group_client = RolesGroupClient(**API_ACCESS_CONFIG)
        roles_group = {
            'name': 'TestRolesGroup',
            'description': 'TestRolesGrou',
            'roles': ["TestRole"]
        }

        result = roles_group_client.create(roles_group)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = roles_group_client.get_by_id(result.content['name'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = roles_group_client.get_by_id('sample-roles-group')
        self.assertTrue(result.response.status == 404)

        result = roles_group_client.search({'description': 'TestRolesGrou'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = roles_group_client.delete(result.content['items'][0]['name'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = roles_group_client.create(roles_group)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        roles_group['description'] += 'p'
        result = roles_group_client.update(roles_group, result.content['name'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = roles_group_client.delete('TestRolesGroup')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        # Tests Cleanup

        result = role_client.delete('TestRole')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = feature_client.delete('TestFeature')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = resource_client.delete(resource_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
