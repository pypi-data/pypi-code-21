import logging
from django.db import models
from django_dragonpay.settings import DRAGONPAY_SAVE_DATA

__all__ = ['DragonpayPayoutUser', 'DragonpayTransaction', 'DragonpayPayout']

logger = logging.getLogger('dragonpay.models')


class DragonpayPayoutUser(models.Model):
    first_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    email = models.CharField(max_length=64)
    birthdate = models.DateField()
    mobile = models.CharField(max_length=24)
    address1 = models.CharField(max_length=32)
    address2 = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=16)
    state = models.CharField(max_length=16)
    zip = models.CharField(max_length=8)

    class Meta:
        app_label = 'django_dragonpay'
        verbose_name = "Payout User"
        verbose_name_plural = "Payout Users"


class DragonpayTransaction(models.Model):
    STATUS_CODES = (
        ('S', 'Success'),
        ('F', 'Failed'),
        ('P', 'Pending'),
        ('U', 'Unknown'),
        ('R', 'Refund'),
        ('K', 'Chargeback'),
        ('V', 'Voided'),
        ('A', 'Authorized'),
        ('E', 'Expired'),
    )

    CURRENCIES = (('PHP', 'Philippine Peso'), ('USD', 'US Dollar'))

    id = models.CharField(
        primary_key=True, max_length=40, verbose_name='Transaction ID')
    token = models.CharField(max_length=40)                 # tokenid id
    refno = models.CharField(max_length=8, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(
        max_length=3, choices=CURRENCIES, default='PHP')
    description = models.CharField(max_length=128)
    email = models.CharField(max_length=40)
    param1 = models.CharField(max_length=80, null=True, blank=True)
    param2 = models.CharField(max_length=80, null=True, blank=True)

    status = models.CharField(max_length=1, choices=STATUS_CODES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_dragonpay'
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __unicode__(self):
        return '%s [%s:%s] %s' % (
            self.get_status_display(), self.id, self.amount, self.email)

    def fetch_status(self):
        '''Query DragonPay for the status of this transaction and update the
        database.'''

        from django_dragonpay.api.soap import get_txn_status
        from django_dragonpay.constants import DRAGONPAY_STATUS_CODES

        status = get_txn_status(self.id)

        if status != self.status:
            logger.info(
                '[%s] status updated to %s',
                self.id, DRAGONPAY_STATUS_CODES[status])

            self.status = status
            self.save(update_fields=['status'])

    @classmethod
    def create_from_dict(cls, details):
        # Check if we should save to database
        if not DRAGONPAY_SAVE_DATA:
            return

        return DragonpayTransaction.objects.create(
            id=details['txn_id'],
            amount=details['amount'],
            currency=details.get('currency') or 'PHP',
            description=details['description'],
            email=details['email'],
            param1=details.get('param1'),
            param2=details.get('param2'),
            token=details.get('token')
        )

    def fetch_ref_no(self, do_update=True):
        from django_dragonpay.api.soap import get_txn_ref_no
        if self.refno:
            # only fetch refno if not yet in database
            return self.refno

        refno = get_txn_ref_no(self.id)

        if refno and do_update:
            self.refno = refno
            self.save(update_fields=['refno'])

        return refno


class DragonpayPayout(models.Model):
    STATUS_CODES = (
        ('S', 'Success'),
        ('F', 'Failed'),
        ('P', 'Pending'),
        ('G', 'In progress'),
        ('V', 'Voided'),
    )

    PROCESSORS = (
        (('BDO', 'Banco De Oro')),
        (('BPI', 'Bank of the Philippine Islands')),
        (('CBC', 'Chinabank')),
        (('EWB', 'East West Bank')),
        (('LBP', 'Land Bank of the Philippines')),
        (('MBTC'), ('Metrobank')),
        (('PNB'), ('Philippine National Bank')),
        (('RCBC'), ('RCBC')),
        (('SBC'), ('Security Bank')),
        (('UBP'), ('Union Bank')),
        (('UCPB'), ('UCPB')),
        (('PSB'), ('PS Bank')),
        (('CEBL'), ('Cebuana Lhuilier')),
        (('GCSH'), ('GCash')),
        (('SMRT'), ('Smart Money')),
    )

    id = models.CharField(
        primary_key=True, max_length=40, verbose_name='Transaction ID')
    refno = models.CharField(max_length=8, null=True, blank=True)

    # For payout registerd user
    user_id = models.CharField(max_length=40, null=True, blank=True)

    # For non-registered, one time payout
    user_name = models.CharField(max_length=32, null=True, blank=True)
    processor_id = models.CharField(
        max_length=8, null=True, blank=True, choices=PROCESSORS)
    processor_detail = models.CharField(max_length=32, null=True, blank=True)
    email = models.CharField(max_length=32, null=True, blank=True)
    mobile = models.CharField(max_length=32, null=True, blank=True)

    # payout details
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=128)
    currency = models.CharField(max_length=3, default='PHP')
    status = models.CharField(max_length=1, choices=STATUS_CODES, default='P')

    created_at = models.DateTimeField(auto_now_add=True)    # timestamp field
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_dragonpay'
        verbose_name = "Payout"
        verbose_name_plural = "Payouts"

    def __unicode__(self):
        return '%s [%s] %s %s' % (
            self.get_status_display(), self.id, self.amount,
            self.user_id or self.user_name)

    @property
    def is_completed(self):
        # we consider the txn complete if it is success/failed/void
        return self.status in ['S', 'F', 'V']

    def fetch_status(self):
        '''Query DragonPay for the status of this transaction and update the
        database.'''

        from django_dragonpay.api.soap import get_payout_txn_status
        from django_dragonpay.constants import DRAGONPAY_STATUS_CODES

        status = get_payout_txn_status(self.id)

        # update the status
        if status and status != self.status:
            logger.info(
                '[%s] status updated to %s',
                self.id, DRAGONPAY_STATUS_CODES[status])

            self.status = status
            self.save(update_fields=['status'])

    @classmethod
    def create_from_dict(cls, details):
        # Check if we should save to database
        if not DRAGONPAY_SAVE_DATA:
            return

        payouts = []
        if isinstance(details, dict):
            # request is for a single payout
            # it may be registered, or non-registered payout user
            logger.debug(
                'Payout txn [%s] saved to database', details['txn_id'])

            return DragonpayPayout.objects.create(
                id=details['txn_id'],
                user_id=details.get('user_id'),
                user_name=details.get('user_name'),
                processor_id=details.get('processor_id'),
                processor_detail=details.get('processor_detail'),
                email=details.get('email'),
                mobile=details.get('mobile'),
                amount=details['amount'],
                description=details['description'],
                currency=details.get('currency') or 'PHP',
                created_at=details['timestamp'],
            )

        elif isinstance(details, list):
            # request is from MultiplePayout; iterate over the details
            for i, detail in enumerate(details):
                logger.debug(
                    '[%d] Payout txn [%s] saved to database',
                    i, details['txn_id'])

                payouts.append(
                    DragonpayPayout.objects.create(
                        id=detail['txn_id'],
                        user_id=detail['user_id'],
                        amount=detail['amount'],
                        description=detail['description'],
                        currency=details.get('currency') or 'PHP',
                        created_at=detail['timestamp'],
                    ))

            return payouts

        else:
            raise Exception('Invalid details type %s', type(details))
