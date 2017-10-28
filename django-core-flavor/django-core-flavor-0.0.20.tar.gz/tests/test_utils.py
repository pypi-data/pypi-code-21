from django.test import TestCase
from django.test.client import RequestFactory

from core_flavor import utils


class UtilsTests(TestCase):

    def test_camel_to_dashed(self):
        self.assertIn('my_test', utils.camel_to_dashed({
            'myTest': {'camelToDashed': True}
        }))

    def test_client_ip(self):
        factory = RequestFactory()
        request = factory.get('/')
        self.assertEqual(utils.get_client_ip(request), '127.0.0.1')

        forwarder_ip = '0.0.0.1'
        request = factory.get('/', HTTP_X_FORWARDED_FOR=forwarder_ip)
        self.assertEqual(utils.get_client_ip(request), forwarder_ip)

    def test_sizeof_fmt(self):
        self.assertEqual(utils.sizeof_fmt(1024 ** 2), '1.0MB')
        self.assertEqual(utils.sizeof_fmt(1024 ** 4), '1.0TB')
