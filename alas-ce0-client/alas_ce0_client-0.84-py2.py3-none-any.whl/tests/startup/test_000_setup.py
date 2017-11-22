# coding=utf-8
import unittest

import time

from sdp_dtv.management.configuration import ConfigurationClient
from sdp_dtv.management.employee import EmployeeClient
from sdp_dtv.management.feature import FeatureClient
from sdp_dtv.management.maintenance import MaintenanceClient
from sdp_dtv.management.role import RoleClient
from sdp_dtv.management.shelf import ShelfCellTemplateClient, ShelfRowTemplateClient
from sdp_dtv.management.user import UserClient
from tests import API_ACCESS_CONFIG, DEPLOY_ENV


class TestSetup(unittest.TestCase):
    def test_startup(self):
        configuration_client = ConfigurationClient(**API_ACCESS_CONFIG)
        file_path = 'config/address-cl.json' if DEPLOY_ENV else '../../config/address-cl.json'

        with open(file_path) as f:
            content = f.read()

        if content:
            result = configuration_client.set('address-cl.json', content)
            self.assertTrue(result.response.status == 204)
            time.sleep(0.5)

        maintenance_client = MaintenanceClient(**API_ACCESS_CONFIG)
        result = maintenance_client.process_operation('address_structure', {'country_code': 'CL'})
        self.assertTrue(result.response.status == 200)


if __name__ == '__main__':
    unittest.main()
