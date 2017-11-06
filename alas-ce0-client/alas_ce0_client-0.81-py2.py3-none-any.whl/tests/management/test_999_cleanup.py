import unittest

import time

from sdp_dtv.management.contact import ContactClient
from sdp_dtv.management.delivery_entity import B2BClient, IntermediateCarrierClient, RegionalPartnerClient
from sdp_dtv.management.delivery_service_level import DeliveryServiceLevelClient
from sdp_dtv.management.employee import EmployeeClient
from sdp_dtv.management.feature import FeatureClient
from sdp_dtv.management.operations_zone import OperationsZoneClient
from sdp_dtv.management.package_template import PackageTemplateClient
from sdp_dtv.management.packaging import PackagingLocationClient
from sdp_dtv.management.product_template import ProductTemplateClient
from sdp_dtv.management.resource import ResourceClient
from sdp_dtv.management.role import RoleClient
from sdp_dtv.management.roles_group import RolesGroupClient
from sdp_dtv.management.shelf import ShelfCellTemplateClient, ShelfRowTemplateClient, ShelfTemplateClient
from sdp_dtv.management.user import UserClient
from sdp_dtv.management.vehicle import CargoVehicleTemplateClient, ShelfCargoVehicleTemplateClient
from tests import API_ACCESS_CONFIG


class TestManagementCleanup(unittest.TestCase):
    def test_cleanup(self):
        user_client = UserClient(**API_ACCESS_CONFIG)
        result = user_client.delete('test')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        roles_group_client = RolesGroupClient(**API_ACCESS_CONFIG)
        result = roles_group_client.delete('TestRolesGroup')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        role_client = RoleClient(**API_ACCESS_CONFIG)
        result = role_client.delete('TestRole')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        feature_client = FeatureClient(**API_ACCESS_CONFIG)
        result = feature_client.delete('TestFeature')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        resource_client = ResourceClient(**API_ACCESS_CONFIG)
        result = resource_client.search({'target': '/target'})
        result = resource_client.delete(result.content['items'][0]['resource_id'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        employee_client = EmployeeClient(**API_ACCESS_CONFIG)
        result = employee_client.delete("22222222-2")
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        shelf_column_client = ShelfCellTemplateClient(**API_ACCESS_CONFIG)
        result = shelf_column_client.delete('C1')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        shelf_row_client = ShelfRowTemplateClient(**API_ACCESS_CONFIG)
        result = shelf_row_client.delete('R1')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        shelf_client = ShelfTemplateClient(**API_ACCESS_CONFIG)
        result = shelf_client.delete('S1')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        cargo_vehicle_client = CargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        result = cargo_vehicle_client.delete('CVT1')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        shelf_cargo_vehicle_client = ShelfCargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        result = shelf_cargo_vehicle_client.delete('SCVT1')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        contact_client = ContactClient(**API_ACCESS_CONFIG)
        result = contact_client.delete('44444444-4')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        chilean_packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)
        result = chilean_packaging_location_client.search({'what3words': 'liner.cooking.montage'})
        result = chilean_packaging_location_client.delete(result.content['items'][0]['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        b2b_client = B2BClient(**API_ACCESS_CONFIG)
        result = b2b_client.delete('33333333-3')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        intermediate_carrier_client = IntermediateCarrierClient(**API_ACCESS_CONFIG)
        result = intermediate_carrier_client.delete('77777777-7')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        regional_partner_client = RegionalPartnerClient(**API_ACCESS_CONFIG)
        result = regional_partner_client.delete('88888888-8')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        package_template_client = PackageTemplateClient(**API_ACCESS_CONFIG)
        result = package_template_client.delete('Box1')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        product_template_client = ProductTemplateClient(**API_ACCESS_CONFIG)
        result = product_template_client.delete('KitPrepagoDTV')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        operations_zone_client = OperationsZoneClient(**API_ACCESS_CONFIG)
        result = operations_zone_client.search({'name': 'RM-Vitacura'})
        result = operations_zone_client.delete(result.content['items'][0]['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        delivery_service_level_client = DeliveryServiceLevelClient(**API_ACCESS_CONFIG)
        result = delivery_service_level_client.search({'name': 'RM-Vitacura'})
        result = delivery_service_level_client.delete(result.content['items'][0]['delivery_service_level_id'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
