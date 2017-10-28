from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OrdersAppConfig(AppConfig):
    name = 'orders'
    verbose_name = _('Orders')

    def ready(self):
        import orders.signals.orders  # NOQA
        import orders.signals.paypal  # NOQA
