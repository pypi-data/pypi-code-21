from django.dispatch import receiver
from django.db.models.signals import pre_save
from countries import models as countries_models

from .. import models
from .. import settings as orders_settings


@receiver(pre_save, sender=models.Order)
def assign_currency_to_order(sender, instance, **kwargs):
    if not hasattr(instance, 'currency'):
        instance.currency = countries_models.Currency.objects.get(
            code=orders_settings.ORDERS_DEFAULT_CURRENCY_CODE
        )
