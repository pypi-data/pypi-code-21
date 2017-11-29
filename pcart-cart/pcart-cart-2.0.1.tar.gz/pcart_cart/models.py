from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.conf import settings
import uuid
from decimal import Decimal
from pcart_customers.models import Customer


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(
        Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='carts')
    customer = models.ForeignKey(
        Customer, verbose_name=_('Customer'), on_delete=models.CASCADE, related_name='carts')

    content = JSONField(_('Content'), default=list, blank=True)
    note = models.TextField(_('Note'), default='', blank=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        unique_together = ['site', 'customer']

    def __str__(self):
        return str(self.customer)

    def items(self):
        from pcart_catalog.models import Product, ProductVariant
        result = self.content
        i = 0
        for item in result:
            item['id'] = i
            i += 1
            if item['item_type'] == 'product':
                item['product'] = Product.objects.get(id=item['item_id'])
                item['object'] = item['product']
            elif item['item_type'] == 'variant':
                item['variant'] = ProductVariant.objects.select_related('product')\
                    .prefetch_related('product__images').get(id=item['item_id'])
                item['product'] = item['variant'].product
                item['object'] = item['variant']
        return result

    def item_count(self):
        return len([x for x in self.content if x['item_type'] in ['product', 'variant']])

    def total_weight(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['weight'])
        return float(result)

    def total_price(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['price'])
        return float(result)

    def change_item_quantity(self, id, quantity, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            _qty = int(quantity)
            if _qty == 0:
                self.remove_item(id, save=False)
            else:
                self.content[id]['quantity'] = _qty
                self.content[id]['line_price'] = float(_qty * Decimal(self.content[id]['price']))
            if save:
                self.save()

    def remove_item(self, id, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            del self.content[id]
            if save:
                self.save()

    def add_item(self, item_id, item_type='product', quantity=1, price=0.00, weight=0, commit=True):
        item = {
            'item_id': item_id,
            'item_type': item_type,
            'quantity': int(quantity),
            'price': float(price),
            'weight': float(weight),
            'line_price': float(Decimal(quantity)*Decimal(price)),
        }
        _append = True
        for i in self.content:
            if i['item_id'] == item_id and i['item_type'] == item_type:
                _append = False
                _qty = Decimal(i['quantity']) + Decimal(quantity)
                i['quantity'] = int(_qty)
                i['price'] = float(price)
                i['line_price'] = float(_qty*Decimal(price))
        if _append:
            self.content.append(item)
        if commit:
            self.save()

    def clear(self, save=True):
        self.content = list()
        self.note = ''
        if save:
            self.save()

    def copy_from(self, another_cart, save=True):
        self.content = another_cart.content
        self.note = another_cart.note
        if save:
            self.save()


class OrderNumberFormat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.OneToOneField(
        Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='order_number_format')

    template = models.CharField(_('Template'), default='P%06d', max_length=20)
    last_number = models.PositiveIntegerField(_('last number'), default=0)

    class Meta:
        verbose_name = _('Order number format')
        verbose_name_plural = _('Order number formats')

    def __str__(self):
        return self.template % self.last_number

    def increase_number(self, delta=1, save=True):
        self.last_number += delta
        if save:
            self.save()
        return self.last_number


class OrderStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=100)
    slug = models.SlugField(_('Slug'))
    weight = models.PositiveIntegerField(_('Weight'), default=0)

    class Meta:
        verbose_name = _('Order status')
        verbose_name_plural = _('Order statuses')
        ordering = ['weight']

    def __str__(self):
        return self.title


def get_default_order_status():
    if OrderStatus.objects.count() == 0:
        try:
            o = OrderStatus.objects.get(slug='submitted')
            return o.pk
        except OrderStatus.DoesNotExist:
            o = OrderStatus(title='Submitted', slug='submitted')
            o.save()
            return o.pk
    else:
        return OrderStatus.objects.first().pk


class Order(models.Model):
    EXPORT_STATUSES = (
        ('notset', _('Not set')),
        ('processing', _('Processing')),
        ('success', _('Success')),
        ('failed', _('Failed')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(_('Number'), max_length=50, unique=True)

    site = models.ForeignKey(
        Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='orders')
    customer = models.ForeignKey(
        Customer, verbose_name=_('Customer'), on_delete=models.CASCADE, related_name='orders')

    content = JSONField(_('Content'), default=list, blank=True)

    shipping_data = JSONField(_('Shipping data'), default=dict, blank=True)
    payment_data = JSONField(_('Payment data'), default=dict, blank=True)

    note = models.TextField(_('Note'), default='', blank=True)

    total_price = models.DecimalField(_('Total price'), max_digits=10, decimal_places=2, default=0.00)
    total_weight = models.FloatField(_('Total weight (kg)'), default=0.0)

    status = models.ForeignKey(OrderStatus, verbose_name=_('Status'), default=get_default_order_status)
    export_status = models.CharField(
        _('Export status'), max_length=70, default='notset', choices=EXPORT_STATUSES,
        help_text=_('Reserved field for integration with third-party software.')
    )

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return self.number

    def _get_total_weight(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['weight'])
        return float(result)

    def _get_total_price(self):
        result = Decimal(0)
        for i in self.content:
            result += Decimal(i['quantity']) * Decimal(i['price'])
        return float(result)

    def save(self, *args, **kwargs):
        self.total_price = self._get_total_price()
        self.total_weight = self._get_total_weight()
        super(Order, self).save(*args, **kwargs)

    def item_count(self):
        return len([x for x in self.content if x['item_type'] in ['product', 'variant']])

    def items(self):
        from pcart_catalog.models import Product, ProductVariant
        result = self.content
        i = 0
        for item in result:
            item['id'] = i
            i += 1
            if item['item_type'] == 'product':
                item['product'] = Product.objects.get(id=item['item_id'])
                item['object'] = item['product']
            elif item['item_type'] == 'variant':
                item['variant'] = ProductVariant.objects.select_related('product')\
                    .prefetch_related('product__images').get(id=item['item_id'])
                item['product'] = item['variant'].product
                item['object'] = item['variant']
        return result

    def send_message(self):
        """Send messages to the customer and moderation team."""
        from pcart_messaging.utils import send_email_message, send_email_to_group
        from pcart_customers.models import User
        from django.conf import settings
        sender = settings.DEFAULT_FROM_EMAIL
        context = {
            'order': self,
        }
        if self.customer.user:
            recipients = [self.customer.user.email]
            send_email_message('order', recipients, sender, context)

        # Looking for a group "order" for sending the info about new order
        send_email_to_group('order_moderation', 'order', sender, context)

    def change_item_quantity(self, id, quantity, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            _qty = int(quantity)
            if _qty == 0:
                self.remove_item(id, save=False)
            else:
                self.content[id]['quantity'] = _qty
                self.content[id]['line_price'] = float(_qty * Decimal(self.content[id]['price']))
            if save:
                self.save()

    def remove_item(self, id, save=True):
        id = int(id)
        if 0 <= id < len(self.content):
            del self.content[id]
            if save:
                self.save()

    def _get_payment_obj(self):
        from django.utils.module_loading import import_string
        method_name = self.payment_data.get('method')
        if method_name:
            for m in settings.PCART_PAYMENT_METHODS:
                if m['name'] == method_name:
                    _class = import_string(m['backend'])
                    _obj = _class(config=m.get('config', {}))
                    return _obj

    def _get_shipping_obj(self):
        from django.utils.module_loading import import_string
        method_name = self.shipping_data.get('method')
        if method_name:
            for m in settings.PCART_SHIPPING_METHODS:
                if m['name'] == method_name:
                    _class = import_string(m['backend'])
                    _obj = _class(config=m.get('config', {}))
                    return _obj

    def get_shipping_info(self, plain_text=False):
        _obj = self._get_shipping_obj()
        html = _obj.render_data(self.shipping_data.get('data', {}), plain_text)
        return html

    def get_payment_info(self, plain_text=False):
        _obj = self._get_payment_obj()
        html = _obj.render_data(self.payment_data.get('data', {}), plain_text)
        return html

    def get_shipping_info_as_text(self):
        return self.get_shipping_info(plain_text=True)

    def get_payment_info_as_text(self):
        return self.get_payment_info(plain_text=True)

    def get_shipping_method_name(self):
        return self.shipping_data.get('method', '')

    def get_payment_method_name(self):
        return self.payment_data.get('method', '')

