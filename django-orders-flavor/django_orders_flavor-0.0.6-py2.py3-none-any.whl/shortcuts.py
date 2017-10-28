from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


def paypal_context(order, request):
    assert hasattr(settings, 'PAYPAL_BUSINESS'), (
        'Missing "PAYPAL_BUSINESS" settings var'
    )

    _uri = request.build_absolute_uri

    return {
        'item_name': _('Order {id}').format(id=order.id.hex),
        'business': settings.PAYPAL_BUSINESS,
        'invoice': order.id.hex,
        'notify_url': _uri(reverse('paypal-ipn')),
        'return_url': _uri('paypal-success'),
        'cancel_return': _uri('paypal-cancel'),
        'currency_code': order.currency.code,
        'custom': order.id.hex,
        'amount': '{:.2f}'.format(order.amount)
    }
