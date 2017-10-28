from django.contrib import admin

from polymorphic import admin as polymorphic_admin
from sorl.thumbnail.admin import AdminImageMixin

from core_flavor.utils import get_model

from . import settings as orders_settings
from . import models


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'amount', 'currency', 'payment_method', 'status',
        'status_changed', 'created')

    list_filter = (
        'user', 'content_type', 'status', 'status_changed', 'created')


@admin.register(models.Item)
class ItemAdmin(AdminImageMixin,
                polymorphic_admin.PolymorphicParentModelAdmin):

    base_model = models.Item
    child_models = [
        get_model(value)
        for value in orders_settings.ORDERS_ITEMS_CHILD_MODELS
    ]

    list_display = ('name', 'sku', 'price', 'tax_rate', 'created')
    list_filter = ('created',)
