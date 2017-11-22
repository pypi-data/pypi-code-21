# coding=utf-8
import time
import unittest

from sdp_dtv.management.shelf import ShelfTemplateClient
from tests import API_ACCESS_CONFIG


class TestShelfApi(unittest.TestCase):
    def test_crud(self):
        shelf_template_client = ShelfTemplateClient(**API_ACCESS_CONFIG)
        shelf_template = {
            'code': 'S1',
            'rows': ['R1']
        }

        result = shelf_template_client.create(shelf_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_template_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_template_client.get_by_id('sample-shelf-row')
        self.assertTrue(result.response.status == 404)

        result = shelf_template_client.search({'code': shelf_template['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_template_client.delete(shelf_template['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = shelf_template_client.create(shelf_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_template['rows'] = ['R1']
        result = shelf_template_client.update(shelf_template, shelf_template['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()