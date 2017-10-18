import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django_extensions.db.fields.json import JSONField
from model_utils import FieldTracker

from .signals import payment_succeed


# https://developer.paypal.com/docs/api/payments/#definition-transaction
class PaypalTransaction(models.Model):
    USD = 'USD'

    CURRENCIES = (
        (USD, USD),
    )

    STATE_CREATED = 'created'
    STATE_APPROVED = 'approved'
    STATE_FAILED = 'failed'

    STATES = (
        (STATE_CREATED, STATE_CREATED),
        (STATE_APPROVED, STATE_APPROVED),
        (STATE_FAILED, STATE_FAILED),
    )

    # request ==================================================================

    # The description of what is being paid for.
    description = models.CharField(max_length=127)

    # item_list.items: The item details.
    # sku[127], name[127], description[127], quantity[10], price[10], currency[3], tax, url
    items = JSONField(default=[])

    # Optional. The merchant-provided ID for the purchase unit.
    reference_id = models.CharField(max_length=256, null=True, blank=True)

    # A free-form field that clients can use to send a note to the payer.（non-transaction field)
    note_to_payer = models.CharField(max_length=165, null=True, blank=True)

    # A free-form field for clients' use.
    custom = models.CharField(max_length=127, null=True, blank=True)

    # paypal的支付id，需要在生成model后，调用api生成Payment对象，然后存入payment.id
    payment_id = models.CharField(max_length=64, null=True, blank=True)

    # The invoice number to track this payment.
    # 没有就不会显示在paypal中，可以用作商户订单号
    invoice_number = models.CharField(max_length=127, null=True, blank=True)

    # The amount to collect.
    # 除了details中的一些特殊的金额，其他都要手动设置，要通过add_item来更新
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCIES)
    amount_details = JSONField(default={})

    # SKIPPED
    # - note_to_payee: An optional note to the recipient of the funds in this transaction.
    # - purchase_order: purchase order is number or id specific to this payment
    # - soft_descriptor: The soft descriptor that is used when charging this funding source. If the string's length is greater than the maximum allowed length, the string is truncated.
    # - payment_options: The payment options requested for this transaction.
    # - notify_url: The URL to send payment notifications. （亲测可以收到通知）
    # - order_url: The URL on the merchant site related to this payment.
    # - related_resources: read only
    # - item_list
    #   + shipping_address
    #   + shipping_method
    #   + shipping_phone_number

    # response only ==================================================================

    # The source of the funds for this payment. Payment method is PayPal Wallet payment, bank direct debit, or direct credit card.
    # 订单成功后返回的数据中获得
    payer_id = models.CharField(max_length=16, null=True, blank=True)
    payer_email = models.EmailField(null=True, blank=True)
    payer_data = JSONField(null=True)

    # payee: The recipient of the funds in this transaction.
    payee_merchant_id = models.CharField(max_length=16, null=True, blank=True)

    # The state of the payment, authorization, or order transaction
    state = models.CharField(max_length=16, choices=STATES, default=STATE_CREATED)

    # customized ==================================================================
    uid = models.CharField(max_length=36, default=uuid.uuid4, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tracker = FieldTracker(fields=['state'])

    def is_succeed(self):
        return self.state == self.STATE_APPROVED

    is_succeed.boolean = True

    def add_item(self, name, currency, price, quantity=1, sku=None, description=None, tax=None):
        item = {
            "name": name,
            "currency": currency,
            "price": "{:.2f}".format(price),
            "quantity": str(quantity),
        }

        if sku:
            item['sku'] = str(sku)

        if description:
            item['description'] = str(description)

        if tax:
            item['tax'] = "{:.2f}".format(tax)

        self.items.append(item)
        self.refresh_amount()

    def refresh_amount(self):
        currencies = set(x['currency'] for x in self.items)
        assert len(currencies) == 1, 'multi currency not supported'

        self.currency = list(currencies)[0]

        self.amount_details['subtotal'] = '{:.2f}'.format(sum(float(x['price']) * float(x['quantity'])
                                                              for x in self.items))

        tax = sum(float(x.get('tax', 0)) for x in self.items)
        if tax:
            self.amount_details['tax'] = '{:.2f}'.format(tax)
        else:
            self.amount_details.pop('tax', None)

        self.amount_total = float('{:.2f}'.format(
            sum(float(v) for v in self.amount_details.values())
        ))

    def to_dict(self):
        data = {
            'amount': {
                "total": "0.00"
            },
            "item_list": {
                "items": [],
            }
        }

        direct_fields = [
            'invoice_number',
            'description',
            'reference_id',
            'custom',
        ]
        for field in direct_fields:
            value = getattr(self, field, None)
            if value:
                data[field] = getattr(self, field)

        data['amount']['total'] = str(self.amount_total)
        data['amount']['currency'] = self.currency
        if self.amount_details:
            data['amount']['details'] = self.amount_details

        data['item_list']['items'] = self.items

        return data

    @classmethod
    def on_post_save(cls, instance: 'PaypalTransaction', raw=None, **kwargs):
        if raw:  # 导入fixture时不运行
            return

        if instance.tracker.has_changed('state') and instance.state == PaypalTransaction.STATE_APPROVED:
            payment_succeed.send(PaypalTransaction, instance=instance)


post_save.connect(PaypalTransaction.on_post_save, PaypalTransaction)
