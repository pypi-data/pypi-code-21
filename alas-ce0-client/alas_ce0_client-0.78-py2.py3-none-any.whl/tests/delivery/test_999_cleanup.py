import time
import unittest

from alas_ce0.delivery.b2c import B2CClient
from alas_ce0.delivery.delivery_order import DeliveryOrderRequestClient, DeliveryOrderClient
from alas_ce0.management.contact import ContactClient
from alas_ce0.management.delivery_entity import B2BClient, RegionalPartnerClient, IntermediateCarrierClient
from alas_ce0.management.employee import EmployeeClient
from alas_ce0.management.operations_zone import OperationsZoneClient
from alas_ce0.management.package_template import PackageTemplateClient
from alas_ce0.management.packaging import PackagingLocationClient
from alas_ce0.management.product_template import ProductTemplateClient
from tests import API_ACCESS_CONFIG


class TestDeliveryCleanup(unittest.TestCase):
    def test_cleanup(self):
        contact_client = ContactClient(**API_ACCESS_CONFIG)
        result = contact_client.delete('44444444-4')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)
        result = packaging_location_client.search({'what3words': 'liner.cooking.montage'})
        result = packaging_location_client.delete(result.content['items'][0]['code'])
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

        operations_zone_client = OperationsZoneClient(**API_ACCESS_CONFIG)
        result = operations_zone_client.search({'name': 'RM-Vitacura'})
        result = operations_zone_client.delete(result.content['items'][0]['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        regional_partner_client = RegionalPartnerClient(**API_ACCESS_CONFIG)
        result = regional_partner_client.delete('88888888-8')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        employee_client = EmployeeClient(**API_ACCESS_CONFIG)
        result = employee_client.delete('22222222-2')
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

        delivery_order_request_client = DeliveryOrderRequestClient(**API_ACCESS_CONFIG)
        result = delivery_order_request_client.search({'product_code': '1234567abcd'})
        result = delivery_order_request_client.delete(result.content['items'][0]['delivery_order_request_id'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        delivery_order_client = DeliveryOrderClient(**API_ACCESS_CONFIG)
        result = delivery_order_client.delete('CLAAAREUMADEtise17031000001')
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        b2c_client = B2CClient(**API_ACCESS_CONFIG)
        result = b2c_client.delete("10101010-1")
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
