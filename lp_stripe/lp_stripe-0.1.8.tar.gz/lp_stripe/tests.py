from parameterized import parameterized

from django.test import TestCase, override_settings
from .conf import Settings
from .client import Client


class SettingsTestCase(TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_default_test_mode(self):
        self.assertEqual(self.settings.mode, Settings.MODE_TEST)

    @override_settings(STRIPE_MODE=Settings.MODE_LIVE)
    def test_can_set_mode(self):
        self.assertEqual(self.settings.mode, Settings.MODE_LIVE)

    @override_settings(STRIPE_TEST_API_KEY='testapikey', STRIPE_API_KEY='apikey')
    def test_fetch_test_mode_api_key(self):
        self.assertEqual(self.settings.api_key, 'testapikey')

    @override_settings(STRIPE_MODE=Settings.MODE_LIVE, STRIPE_TEST_API_KEY='testapikey', STRIPE_API_KEY='apikey')
    def test_fetch_live_mode_api_key(self):
        self.assertEqual(self.settings.api_key, 'apikey')


@override_settings(STRIPE_TEST_API_KEY='sk_test_Eo1tQw3uuPrl8uG6kUZ8rjcl')
class ClientTestCase(TestCase):
    def setUp(self):
        self.settings = Settings()
        self.client = Client(api_key=self.settings.api_key)
        self.customer_data = {
            'description': 'Test Customer from django-rest-stripe UnitTest',
            'source': 'tok_amex'
        }
        self.created_customers = []

    def tearDown(self):
        for customer in self.created_customers:
            customer.delete()

    def test_can_create_customer(self):
        try:
            customer = self.client.create_customer(**self.customer_data)
            self.created_customers.append(customer)
        except Exception as e:
            self.fail('Exception was raised: %s' % e)

    def test_can_subscribe_customer(self):
        customer = self.client.create_customer(**self.customer_data)
        self.created_customers.append(customer)
        try:
            subscription = self.client.create_subscription(customer=customer.stripe_id, plan='gold')
        except Exception as e:
            self.fail('Exception was raised: %s' % e)

