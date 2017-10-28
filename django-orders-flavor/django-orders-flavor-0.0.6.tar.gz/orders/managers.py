from django.db import models

from polymorphic.manager import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet

from core_flavor import managers as core_managers


__all__ = ['ItemManager', 'OrderManager']


class BaseItemManager(PolymorphicManager):
    pass


class ItemQuerySet(PolymorphicQuerySet, core_managers.SoftDeletableQuerySet):
    pass


ItemManager = BaseItemManager.from_queryset(ItemQuerySet)


class BaseOrderManager(models.Manager):
    pass


class OrderQuerySet(models.QuerySet):

    def pending(self):
        return self.filter(status=self.model.PENDING)

    def paid(self):
        return self.filter(status=self.model.PAID)


OrderManager = BaseOrderManager.from_queryset(OrderQuerySet)
