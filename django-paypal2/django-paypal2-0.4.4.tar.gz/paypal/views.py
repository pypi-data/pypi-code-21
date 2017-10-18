"""
原则上需要定义三个view name：
    - paypal_redirect
    - paypal_return
    - paypal_cancel

Example urlpatterns
-------------------

urlpatterns = [
    url('^redirect/(?P<pk>.*?)/$', PaypalRedirectView.as_view(), name='paypal_redirect'),
    url('^return/$', PaypalReturnView.as_view(), name='paypal_return'),
    url('^cancel/$', PaypalCancelView.as_view(), name='paypal_cancel'),
]
"""
import logging
import pprint

import paypalrestsdk
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from paypal.models import PaypalTransaction

log = logging.getLogger("django-paypal2.views")


def _get_api():
    conf = settings.PAYPAL.copy()
    if conf.pop('sandbox', False):
        conf['mode'] = 'sandbox'
    else:
        conf['mode'] = 'live'
    return paypalrestsdk.Api(conf)


def example_paypal_create_view(request):
    """  创建transaction的样例 """
    tx = PaypalTransaction(description="hello")
    tx.add_item("vpn", 'USD', 1.11)
    tx.save()

    return redirect('paypal_redirect', pk=tx.pk)


class PaypalRedirectView(View):
    """
    他人生成PaypalTransaction以后，跳转到本view就能重定向到paypal，继续完成支付流程
    样例见： example_paypal_create_view
    """

    def get_return_url(self):
        """ 定义从paypal支付成功以后返回的URL，按需定义 """
        return settings.PAYPAL['SERVER_URL'] + reverse('paypal_return')

    def get_cancel_url(self):
        """ 定义用户取消paypal支付时，返回的页面URL，按需定义 """
        return settings.PAYPAL['SERVER_URL'] + reverse('paypal_cancel')

    def handle_redirect(self, redirect_url):
        """ 得到paypal支付地址以后，定义如何跳转（默认为直接跳转，可以自己改成打开loading页面，用JS跳转 """
        return redirect(redirect_url)

    def payment_create_error(self, payment):
        """ 创建支付失败时的response，按需定义 """
        print("handle_payment_create_error", payment.error)
        return HttpResponseServerError()

    def get(self, request, uid):
        tx = get_object_or_404(PaypalTransaction, uid=uid, state=PaypalTransaction.STATE_CREATED)

        if tx.payment_id:
            payment = paypalrestsdk.Payment.find(tx.payment_id, api=_get_api())
        else:
            params = self.make_params(tx)
            payment = paypalrestsdk.Payment(params, api=_get_api())
            ok = payment.create()
            if not ok:
                return self.payment_create_error(payment)

            tx.payment_id = payment.id
            tx.save()

        for link in payment.links:
            if link.method == 'REDIRECT':
                return self.handle_redirect(link.href)

    def make_params(self, tx):
        params = {
            'intent': 'sale',
            'payer': {
                'payment_method': 'paypal',
            },
            "transactions": [
                tx.to_dict(),
            ],
            "redirect_urls": {
                "return_url": self.get_return_url(),
                "cancel_url": self.get_cancel_url(),
            }
        }

        if tx.note_to_payer:
            params['note_to_payer'] = tx.note_to_payer

        return params


class PaypalReturnView(View):
    """
    从paypal支付成功以后，回来的页面，
    页面自己会处理transaction成功的逻辑，成功以后会发送 payment_succeed signal
    业务逻辑只需要connect payment_succeed，然后做相应的处理即可
    """

    template_name = 'paypal/return.html'

    def payment_succeed(self, tx):
        """ 支付成功以后的返回结果，按需定义 """
        return render(self.request, self.template_name, context=dict(transaction=tx))

    def payment_execute_error(self, payment):
        """ 执行支付失败后的返回结果，按需定义 """
        print("handle_payment_execute_error", payment.error)
        return HttpResponseServerError()

    def get(self, request):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')

        if not payment_id or not payer_id:
            return HttpResponseBadRequest()

        tx = get_object_or_404(PaypalTransaction, payment_id=payment_id)
        if tx.state == tx.STATE_APPROVED:
            return self.payment_succeed(tx)

        payment = paypalrestsdk.Payment.find(payment_id, api=_get_api())
        if payment.state != tx.STATE_APPROVED:
            ok = payment.execute({'payer_id': payer_id})
            if not ok:
                return self.payment_execute_error(payment)

        tx.state = payment.state
        tx.payer_id = payment.payer.payer_info.payer_id
        tx.payer_email = payment.payer.payer_info.email
        tx.payer_data = payment.payer.to_dict()

        if payment.transactions[0].payee:
            tx.payee_merchant_id = payment.transactions[0].payee.merchant_id
        else:
            log.warning("missing payee, data: %s", pprint.pformat(payment))
        tx.save()  # post_save 时，如果初次成功，会抛 payment_succeed signal

        return self.payment_succeed(tx)


class PaypalCancelView(TemplateView):
    template_name = 'paypal/cancel.html'
