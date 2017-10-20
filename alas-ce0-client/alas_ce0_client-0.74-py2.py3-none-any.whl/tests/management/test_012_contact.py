# coding=utf-8
import time
import unittest

from sdp_dtv.management.contact import ContactClient
from tests import API_ACCESS_CONFIG


class TestContactApi(unittest.TestCase):
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

        result = contact_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = contact_client.search({'code': contact['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        result = contact_client.get_by_id('sample-contact')
        self.assertTrue(result.response.status == 404)

        result = contact_client.delete(contact['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = contact_client.create(contact)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        contact['web'] += '/test'

        result = contact_client.update(contact, contact['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()