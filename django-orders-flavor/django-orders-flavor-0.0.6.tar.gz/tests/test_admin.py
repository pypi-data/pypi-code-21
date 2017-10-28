from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from orders import admin
from orders import models


class MockRequest:
    pass


request = MockRequest()


class AdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()

    def test_admin_item(self):
        model_admin = admin.ItemAdmin(models.Item, self.site)
        self.assertIn('name', model_admin.get_fields(request))

    def test_admin_order(self):
        model_admin = admin.OrderAdmin(models.Order, self.site)
        self.assertIn('user', model_admin.get_fields(request))
