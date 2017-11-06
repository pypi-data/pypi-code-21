# coding=utf-8
import calendar
import time
import unittest

import datetime

from alas_ce0.delivery.delivery_order import DeliveryOrderStatusType

from alas_ce0.management.delivery_entity import IntermediateCarrierClient

from alas_ce0.delivery.delivery_order import DeliveryOrderClient, DeliveryOrderProcessType, DeliveryOrderStakeholderType

from alas_ce0.management.contact import ContactClient

from alas_ce0.management.employee import EmployeeClient

from alas_ce0.management.service_level import ServiceLevelClient

from alas_ce0.management.delivery_entity import RegionalPartnerClient

from alas_ce0.management.geographic_coverage import GeographicCoverageClient

from alas_ce0.management.distribution_zone import DistributionZoneClient

from alas_ce0.management.cross_docking import CrossDockingLocationClient

from alas_ce0.management.packaging import PackagingLocationClient

from alas_ce0.management.product_template import ProductTemplateClient

from alas_ce0.management.package_template import PackageTemplateClient

from alas_ce0.delivery.b2c import B2CClient

from alas_ce0.management.delivery_entity import B2BClient

from config import API_ACCESS_CONFIG


class TestDeliveryOrderApi(unittest.TestCase):
    def test_crud(self):
        # Tests Setup

        contact_client = ContactClient(**API_ACCESS_CONFIG)
        contact = {
            'code': '44444444-4',
            'first_name': 'Contact FirstName',
            'last_name': 'Contact LastName',
            'land_line': '221345678',
            'mobile_phone': '921345678',
            'email': 'contact@gmail.com',
            'web': 'http://www.contact.com'
        }

        result = contact_client.create(contact)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        b2c_client = B2CClient(**API_ACCESS_CONFIG)
        b2c = {
            "code": "10101010-1",
            "first_name": "Joh",
            "last_name": "Doe",
            "mobile_phone": "912345678",
            "email": "john.doe@gmail.com"
        }

        result = b2c_client.create(b2c)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        employee_client = EmployeeClient(**API_ACCESS_CONFIG)
        employee = {
            'first_name': 'First Nam',
            'last_name': 'Last Name',
            'code': '22222222-2',
            'birth_date': '1991-01-01',
            'gender': 1,
            'internal_code': '1',
            'status': 1
        }

        result = employee_client.create(employee)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        employee['code'] = '21212121-5'
        result = employee_client.create(employee)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)
        packaging_location = {
            "code": "Directv-Fijo-Test",
            "type": 1,
            "location":{
                "country_code": "CL",
                "zone_type": 1,
                "geo_coding": "Avenida Vitacura 4380, Vitacura, Chile",
                "geo_location": {
                    "lat": -33.398823,
                    "lon": -70.588274
                },
                "what3words": "liner.cooking.montage",
                "reference": "En la esquina de Vitacura con Américo Vespucio",
                "structure_id": 13132,
                "sector": "",
                "street": "Vitacura",
                "number": "4380",
            },
            "contact": "44444444-4",
        }

        result = packaging_location_client.create(packaging_location)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        b2b_client = B2BClient(**API_ACCESS_CONFIG)
        b2b = {
            'code': '33333333-3',
            'name': 'Directv',
            'location': {
                'country_code': 'CL',
                'zone_type': 1,
                'geo_coding': 'Avenida Vitacura 4380, Vitacura, Chile',
                'geo_location': {
                    'lat': -33.398823,
                    'lon': -70.588274
                },
                'what3words': 'liner.cooking.montage',
                'reference': 'En la esquina de Vitacura con Américo Vespucio',
                'structure_id': 13132,
                'street': 'Vitacura',
                'number': '4380',
                'sector': '',
            },
            'packaging_locations': [result.content['code']],
            'business_activity': 'Televisión Satelital',
            'internal_code': '1'
        }

        result = b2b_client.create(b2b)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        package_template_client = PackageTemplateClient(**API_ACCESS_CONFIG)
        package_template = {
            "code": "Box1-Test",
            "weight": 21.25,
            "width": 11.5,
            "height": 11.3,
            "depth": 21.4,
            "box_type": 1
        }

        result = package_template_client.create(package_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        product_template_client = ProductTemplateClient(**API_ACCESS_CONFIG)
        product_template = {
            "code": "KitPrepagoDTV-Test",
            "name": "Kit Prepago",
            "description": "Kit Prepago",
            "provider_code": "33333333-3",
            "provider_name": "Directv",
            "weight": 20.25,
            "width": 10.5,
            "height": 15.3,
            "depth": 20.4,
            "box_type": 1,
            'packaging_location_code': 'Directv-Fijo-Test'
        }

        result = product_template_client.create(product_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        cross_docking_location_client = CrossDockingLocationClient(**API_ACCESS_CONFIG)
        chilean_cross_docking_location = {
            "code": "Bodega01-SCL-Test",
            "location": {
                "country_code": "CL",
                "zone_type": 1,
                "geo_coding": "Avenida Vitacura 4380, Vitacura, Chile",
                "geo_location": {
                    "lat": -33.398823,
                    "lon": -70.588274
                },
                "what3words": "liner.cooking.montage",
                "reference": "En la esquina de Vitacura con Américo Vespucio",
                "structure_id": 13132,
                "sector": "",
                "street": "Vitacura",
                "number": "4380",
            }
        }

        result = cross_docking_location_client.create(chilean_cross_docking_location)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        distribution_zone_client = DistributionZoneClient(**API_ACCESS_CONFIG)
        distribution_zone = {
            "code": "RM-01-Test",
            "description": "Zona de Distribición 1 de Región Metropolitan",
            "cross_docking_locations": ["Bodega01-SCL-Test"]
        }

        result = distribution_zone_client.create(distribution_zone)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        geographic_coverage_client = GeographicCoverageClient(**API_ACCESS_CONFIG)
        geographic_coverage = {
            "address_structure_id": 13132,
            "distribution_zone_code": distribution_zone['code']
        }

        result = geographic_coverage_client.create(geographic_coverage)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        regional_partner_client = RegionalPartnerClient(**API_ACCESS_CONFIG)
        regional_partner = {
            'code': '88888888-8',
            'name': 'Last Mile Cargo',
            'location': {
                'country_code': 'CL',
                'zone_type': 1,
                'geo_coding': 'Avenida Vitacura 4380, Vitacura, Chile',
                'geo_location': {
                    'lat': -33.398823,
                    'lon': -70.588274
                },
                'what3words': 'liner.cooking.montage',
                'reference': 'En la esquina de Vitacura con Américo Vespucio',
                'structure_id': 13132,
                'street': 'Vitacura',
                'number': '4380',
                'sector': '',
            },
            'distribution_zone_codes': [distribution_zone['code']],
            'internal_code': '1'
        }

        result = regional_partner_client.create(regional_partner)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        service_level_client = ServiceLevelClient(**API_ACCESS_CONFIG)
        service_level = {
            "product_template_code": product_template['code'],
            "distribution_zone_code": distribution_zone['code'],
            "b2b_delivery": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "b2b_reception": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "fixed_packaging": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "mobile_packaging": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "carrier_dispatch": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "carrier_delivery": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "ser_reception": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "vehicle_load": {
                "time_interval": 1,
                "failure_rate": 10
            },
            "b2c_delivery": {
                "time_interval": 1,
                "failure_rate": 10
            },
        }

        result = service_level_client.create(service_level)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)
        service_level_id = result.content['service_level_id']

        intermediate_carrier_client = IntermediateCarrierClient(**API_ACCESS_CONFIG)
        intermediate_carrier = {
            'code': '77777777-7',
            'name': 'Rapid Cargo',
            'location': {
                'country_code': 'CL',
                'zone_type': 1,
                'geo_coding': 'Avenida Vitacura 4380, Vitacura, Chile',
                'geo_location': {
                    'lat': -33.398823,
                    'lon': -70.588274
                },
                'what3words': 'liner.cooking.montage',
                'reference': 'En la esquina de Vitacura con Américo Vespucio',
                'structure_id': 13132,
                'street': 'Vitacura',
                'number': '4380',
                'sector': '',
            },
            'delivery_coverages': [
                {'address_structure_id': 13132, 'delivery_skill': 4}
            ]
        }

        result = intermediate_carrier_client.create(intermediate_carrier)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        # DeliveryOrder Tests

        delivery_order_client = DeliveryOrderClient(**API_ACCESS_CONFIG)
        delivery_order = {
            "code": "CLAAAREUMADEtise17031000001",
            "packages": [
                {
                    "code": "se2222222217031000001U",
                    "package_template_code": "Box1-Test",
                    "status": 1,
                    "products": [
                        {
                            "code": "1234567abcd",
                            "product_template_code": "KitPrepagoDTV-Test",
                        }
                    ]
                }
            ],
            "sender_code": "33333333-3",
            "receiver_code": "10101010-1",
            "status": 1,
            "statuses": [1],
            "priority": 1,
            "receiver_employee_code": "22222222-2",
            "packager_employee_code": "22222222-2",
            "packaging_location_code": "Directv-Fijo-Test",
            "dispatcher_employee_code": "22222222-2",
            "intermediate_carrier_code": "77777777-7",
            "regional_partner_code": "88888888-8",
            "controller_employee_code": "22222222-2",
            "messenger_employee_code": "22222222-2",
            "delivery_manager_code": "22222222-2",
            "destination": {
                "country_code": "CL",
                "structure_id": 16500,
                "street": "Vitacura",
                "number": "4380",
                "local": "piso 15",
                "geo_coding": "Avenida Vitacura 4380, Vitacura",
                "geo_location": {
                    "lat": -33.398823,
                    "lon": -70.588274
                },
                "what3words": "liner.cooking.montage"
            },
            "time_info": {
                "b2b_delivery_expected": "2017-01-05T10:00:00",
                "b2b_delivery_actual": "2017-01-05T10:01:00",
                "b2b_reception_expected": "2017-01-05T11:00:00",
                "b2b_reception_actual": "2017-01-05T11:01:00",
                "packaging_expected": "2017-01-05T12:00:00",
                "packaging_actual": "2017-01-05T12:01:00",
                "carrier_dispatch_expected": "2017-01-05T13:00:00",
                "carrier_dispatch_actual": "2017-01-05T13:01:00",
                "carrier_delivery_expected": "2017-01-05T14:00:00",
                "carrier_delivery_actual": "2017-01-05T14:01:00",
                "ser_reception_expected": "2017-01-05T15:00:00",
                "ser_reception_actual": "2017-01-05T15:01:00",
                "vehicle_load_expected": "2017-01-05T16:00:00",
                "vehicle_load_actual": "2017-01-05T16:01:00",
                "b2c_delivery_expected": "2017-01-05T17:00:00",
                "b2c_delivery_actual": "2017-01-05T17:01:00",
            },
        }

        result = delivery_order_client.create(delivery_order)
        self.assertTrue(result.response.status == 200 and result.content)
        delivery_order_id = result.content['delivery_order_id']
        time.sleep(1)

        result = delivery_order_client.get_by_id(delivery_order_id)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        result = delivery_order_client.get_by_id('123456')
        self.assertTrue(result.response.status == 404)
        time.sleep(1)

        result = delivery_order_client.search({'sender_name': 'Directv'})
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        result = delivery_order_client.delete(delivery_order_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = delivery_order_client.create(delivery_order)
        delivery_order_id = result.content['delivery_order_id']
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        delivery_order['time_info']['b2b_delivery_actual'] = "2017-01-05T10:02:00"
        result = delivery_order_client.update(delivery_order, delivery_order_id)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        start = datetime.datetime.strptime('2017-01-05', "%Y-%m-%d").date()
        first_weekday, days_num = calendar.monthrange(start.year, start.month)

        result = delivery_order_client.get_agenda(
            start.replace(day=1).strftime("%Y-%m-%d"),
            start.replace(day=days_num).strftime("%Y-%m-%d"),
            [DeliveryOrderProcessType.Packaging.value, DeliveryOrderProcessType.B2cDelivery.value], {
                DeliveryOrderStakeholderType.Sender.value: '33333333-3',
                DeliveryOrderStakeholderType.RegionalPartner.value: '33333333-3'
            }
        )
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        result = delivery_order_client.change_planning(
            delivery_order_id, {'change_info': {'receiver_employee_code': '21212121-5'}}
        )
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(1)

        result = delivery_order_client.change_status(
            delivery_order_id, {'status': DeliveryOrderStatusType.PlanningApproved.value}
        )
        self.assertTrue(result.response.status == 200)
        time.sleep(1)

        result = delivery_order_client.delete(delivery_order_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        # Tests Cleanup

        result = b2b_client.delete('33333333-3')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = intermediate_carrier_client.delete('77777777-7')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = regional_partner_client.delete('88888888-8')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = employee_client.delete('22222222-2')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = employee_client.delete('21212121-5')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = b2c_client.delete("10101010-1")
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = packaging_location_client.delete(packaging_location['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = service_level_client.delete(service_level_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = distribution_zone_client.delete("RM-01-Test")
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = cross_docking_location_client.delete("Bodega01-SCL-Test")
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = geographic_coverage_client.delete(13132)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = package_template_client.delete('Box1-Test')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = product_template_client.delete('KitPrepagoDTV-Test')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = contact_client.delete('44444444-4')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
