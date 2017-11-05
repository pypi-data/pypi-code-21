from django.apps import AppConfig
from django.conf import settings

from .utils.delivery import initiate_delivery_manager
from .utils.payment import initiate_payment_manager


class ShopConfig(AppConfig):
    name = 'django_shop'
    verbose_name = 'Магазин'

    def ready(self):
        initiate_payment_manager(getattr(settings, 'SHOP_PAYMENT_HOOKS', {}))
        initiate_delivery_manager(getattr(settings, 'SHOP_DELIVERY_HOOKS', {}))
