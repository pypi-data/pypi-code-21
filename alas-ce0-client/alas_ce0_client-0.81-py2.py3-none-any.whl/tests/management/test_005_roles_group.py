# coding=utf-8
import unittest

import time
from sdp_dtv.management.feature import FeatureClient
from sdp_dtv.management.role import RoleClient
from sdp_dtv.management.roles_group import RolesGroupClient
from tests import API_ACCESS_CONFIG


class TestRoleApi(unittest.TestCase):
    def test_crud(self):
        roles_client = RoleClient(**API_ACCESS_CONFIG)

        result = roles_client.search({'description': 'TestRole'})
        self.assertTrue(result.response.status == 200 and result.content)

        roles_group_client = RolesGroupClient(**API_ACCESS_CONFIG)
        roles_group = {
            'name': 'TestRolesGroup',
            'description': 'TestRolesGrou',
            'roles': [result.content['items'][0]['name']]
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


if __name__ == '__main__':
    unittest.main()
