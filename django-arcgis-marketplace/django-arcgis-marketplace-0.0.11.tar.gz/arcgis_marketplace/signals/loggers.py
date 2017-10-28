import logging

from django.dispatch import receiver
from orders.signals import order_succeeded


logger = logging.getLogger(__name__)


@receiver(order_succeeded)
def order_succeeded_logger(sender, order, *args, **kwargs):
    logger.debug('Order {} succeeded'.format(order.id))
