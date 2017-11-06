# coding=utf-8
import time
import unittest

from sdp_dtv.management.package_template import PackageTemplateClient
from tests import API_ACCESS_CONFIG


class TestPackageTemplateApi(unittest.TestCase):
    def test_crud(self):
        package_template_client = PackageTemplateClient(**API_ACCESS_CONFIG)
        package_template = {
            "code": "Box1",
            "weight": 21.25,
            "width": 11.5,
            "height": 11.3,
            "depth": 21.4,
            "box_type": 1
        }

        result = package_template_client.create(package_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        package_template_code = result.content['code']
        result = package_template_client.get_by_id(package_template_code)
        self.assertTrue(result.response.status == 200 and result.content)

        result = package_template_client.get_by_id('sample-package-template')
        self.assertTrue(result.response.status == 404)

        result = package_template_client.search({'code': 'Box1'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = package_template_client.delete(result.content['items'][0]['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = package_template_client.create(package_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        package_template['width'] = 11.6
        result = package_template_client.update(package_template, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()