# coding=utf-8
import time
import unittest

from alas_ce0.management.resource import ResourceClient

from config import API_ACCESS_CONFIG


class TestResourceApi(unittest.TestCase):
    def test_crud(self):
        # Resource Tests

        resource_client = ResourceClient(**API_ACCESS_CONFIG)
        resource = {
            'description': 'TestResourc',
            'target': '/target'
        }

        result = resource_client.create(resource)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)
        resource_id = result.content['resource_id']

        result = resource_client.get_by_id(result.content['resource_id'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = resource_client.get_by_id('sample-resource')
        self.assertTrue(result.response.status == 404)

        result = resource_client.search({'description': 'TestResourc'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = resource_client.delete(result.content['items'][0]['resource_id'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = resource_client.create(resource)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        resource['description'] += 'e'
        result = resource_client.update(resource, result.content['resource_id'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = resource_client.delete(resource_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()