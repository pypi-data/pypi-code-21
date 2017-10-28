from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils import models as u_models

from polymorphic.models import PolymorphicModel
from sorl.thumbnail import ImageField

from core_flavor import models as core_models
from core_flavor.urls import reverse_host

from . import managers
from . import settings as orders_settings


class AbstractItem(models.Model):
    price = models.FloatField(validators=[MinValueValidator(0)])
    tax_rate = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)])

    class Meta:
        abstract = True

    @property
    def is_free(self):
        return self.price == 0

    @property
    def amount(self):
        return self.price * (1 + self.tax_rate / 100)


class Item(AbstractItem,
           PolymorphicModel,
           core_models.SoftDeletableModel,
           core_models.TimeStampedUUIDModel):

    sku = models.CharField(max_length=64, db_index=True, blank=True)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    image = ImageField(
        _('image'),
        blank=True,
        upload_to=core_models.UUIDUploadTo(
            orders_settings.ORDERS_UPLOAD_THUMBNAILS_TO
        ))

    objects = managers.ItemManager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name

    @property
    def content_type(self):
        return '{app_label}.{model_name}'.format(
            app_label=self._meta.app_label,
            model_name=self._meta.model_name)

    @property
    def comma_separated_tags(self):
        return ','.join(self.tags.names())


class ItemInOrder(AbstractItem, core_models.TimeStampedUUIDModel):
    item = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT,
        verbose_name=_('item'))

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='items_in_order',
        verbose_name=_('order'))

    quantity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "{self.item} <{self.order.id.hex}>".format(self=self)

    @property
    def amount(self):
        return self.quantity * super().amount


class Order(u_models.StatusModel, core_models.TimeStampedUUIDModel):
    PAID = 'paid'
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    DENIED = 'denied'

    STATUS = Choices(
        (PENDING, _('Pending')),
        (PAID, _('Paid')),
        (CANCELLED, _('Cancelled')),
        (DENIED, _('Denied'))
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('user'))

    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_('payment method type'))

    object_id = models.CharField(
        blank=True,
        db_index=True,
        max_length=64,
        verbose_name=_('payment method id'))

    payment_method = GenericForeignKey(
        'content_type',
        'object_id')

    amount = models.FloatField(
        _('amount'),
        default=.0,
        validators=[MinValueValidator(0)])

    items = models.ManyToManyField(
        'Item',
        through='ItemInOrder',
        verbose_name=_('items'))

    currency = models.ForeignKey(
        'countries.Currency',
        on_delete=models.PROTECT,
        verbose_name=_('currency'))

    objects = managers.OrderManager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "{self.id.hex} <{self.user}> ({self.amount})".format(self=self)

    def get_absolute_url(self):
        return reverse_host(
            'orders-api:v1:order-detail',
            args=(self.id.hex,),
            **orders_settings.FLAVOR_REVERSE_EXTRA_KWARGS)

    def _get_amount(self):
        return sum(item.amount for item in self.items_in_order.all())
