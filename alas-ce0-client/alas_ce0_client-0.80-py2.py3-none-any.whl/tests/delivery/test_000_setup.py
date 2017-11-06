# coding=utf-8
import unittest

import time
from alas_ce0.management.contact import ContactClient
from alas_ce0.management.delivery_entity import B2BClient, RegionalPartnerClient, IntermediateCarrierClient
from alas_ce0.management.employee import EmployeeClient
from alas_ce0.management.operations_zone import OperationsZoneClient
from alas_ce0.management.package_template import PackageTemplateClient
from alas_ce0.management.packaging import PackagingLocationClient
from alas_ce0.management.product_template import ProductTemplateClient


class TestSetup(unittest.TestCase):
    def test_crud(self):
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
        time.sleep(0.5)

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
        time.sleep(0.5)

        chilean_packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)
        chilean_packaging_location = {
            "code": "Directv-Fijo",
            "type": 1,
            "product_receiver_code": result.content["code"],
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

        result = chilean_packaging_location_client.create(chilean_packaging_location)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        b2b_client = B2BClient(**API_ACCESS_CONFIG)
        chilean_b2b = {
            'code': '33333333-3',
            'name': 'Directv',
            'short_name': 'DTV',
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
            'business_activity': 'Televisión Satelital'
        }

        result = b2b_client.create(chilean_b2b)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        intermediate_carrier_client = IntermediateCarrierClient(**API_ACCESS_CONFIG)
        chilean_intermediate_carrier = {
            'code': '77777777-7',
            'name': 'Rapid Cargo',
            'short_name': 'RPC',
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
            }
        }

        result = intermediate_carrier_client.create(chilean_intermediate_carrier)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        operations_zone_client = OperationsZoneClient(**API_ACCESS_CONFIG)
        chilean_operations_zone = {
            'code': 'RM-Vitacura',
            'type': 1,
            'name': 'RM-Vitacura',
            'description': 'Zona de Operaciones en Vitacura, Región Metropolitaana',
            'structure_id': 13132
        }

        result = operations_zone_client.create(chilean_operations_zone)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        regional_partner_client = RegionalPartnerClient(**API_ACCESS_CONFIG)
        chilean_regional_partner = {
            'code': '88888888-8',
            'name': 'Last Mile Cargo',
            'short_name': 'LMC',
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
            'operations_zone': result.content['code']
        }

        result = regional_partner_client.create(chilean_regional_partner)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

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

        product_template_client = ProductTemplateClient(**API_ACCESS_CONFIG)
        product_template = {
            "code": "KitPrepagoDTV",
            "name": "Kit Prepago",
            "description": "Kit Prepago",
            "provider_code": "33333333-3",
            "provider_name": "Directv",
            "weight": 20.25,
            "width": 10.5,
            "height": 15.3,
            "depth": 20.4,
            "box_type": 1,
            'packaging_location_code': 'Directv-Fijo'
        }

        result = product_template_client.create(product_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
