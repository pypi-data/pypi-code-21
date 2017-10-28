from django.test import TestCase
from orders import factories


class ModelsTests(TestCase):

    def test_ietm_str(self):
        item = factories.ItemFactory()
        self.assertEqual(str(item), item.name)

    def test_order_str(self):
        order = factories.OrderFactory()
        self.assertTrue(str(order).startswith(order.id.hex))
