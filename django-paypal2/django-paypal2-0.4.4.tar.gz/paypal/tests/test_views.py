from django.test import RequestFactory, TestCase

from paypal.models import PaypalTransaction
from paypal.views import PaypalRedirectView


class PaypalRedirectViewTest(TestCase):
    def test_create(self):
        tx = PaypalTransaction(description="hello")
        tx.add_item("vpn", 'USD', 1.11)
        tx.save()

        view = PaypalRedirectView.as_view()
        factory = RequestFactory()
        req = factory.get('/')

        resp = view(req, uid=tx.uid)
        self.assertTrue('paypal' in resp.url, '跳转到paypal')