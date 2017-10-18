from unittest.mock import Mock

from django.test import TestCase

from paypal.models import PaypalTransaction
from paypal.signals import payment_succeed


class PaypalTransactionTest(TestCase):
    def test_add_item(self):
        tx = PaypalTransaction()

        tx.add_item('simple', 'USD', 0.233)
        tx.add_item('hello', 'USD', 1.01,
                    quantity=3,
                    sku='HL',
                    description='test item',
                    tax=0.07)
        self.assertEqual(tx.currency, 'USD')
        self.assertEqual(str(tx.amount_total), '3.33')
        self.assertEqual(tx.amount_details['subtotal'], '3.26')
        self.assertEqual(tx.amount_details['tax'], '0.07')

    def test_signal_payment_succeed(self):
        tx = PaypalTransaction()
        tx.add_item('simple', 'USD', 0.233)
        tx.save()

        mock = Mock()
        payment_succeed.connect(mock)

        tx.state = PaypalTransaction.STATE_APPROVED
        tx.save()
        self.assertEqual(mock.call_count, 1)

        tx.save()
        self.assertEqual(mock.call_count, 1, '只有切换到APPROVED的时候才抛signal')
