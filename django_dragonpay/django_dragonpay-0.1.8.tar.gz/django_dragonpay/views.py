import logging

from django.views import generic
from django.conf import settings

from django_dragonpay.forms import *
from django_dragonpay.models import DragonpayTransaction, DragonpayPayout

logger = logging.getLogger('dragonpay.views')


__all__ = ['DragonpayCallbackBaseHandler', 'DragonpayPayoutBaseHandler']


class DragonpayCallbackBaseHandler(generic.View):
    '''Base view to handle Dragonpay callback transactions that
    updates the transactions in database.

    Usage:
        Inherit the class based view and implement your
        own GET and POST handlers

        class MyDragonpayCallback(DragonpayCallback):
            allow_invalid_data = False  # raise Error if data is invalid

            def get(self, request, *args, **kwargs):
                # the processed form may be access via
                self.form

                # do your stuff here
                pass

            def post(self, request, *args, **kwargs)
                pass
    '''

    allow_invalid_data = True    # should we crash if the data is invalid?
    update_on_GET = False        # should we update txns on GET request?

    def dispatch(self, *args, **kwargs):
        # if DRAGONPAY_SAVE_DATA settings is True, update the
        # DragonpayTransaction row for this transaction
        self.form = DragonpayCallbackForm(
            self.request.POST or self.request.GET)

        if not self.form.is_valid():
            logger.error(
                'Invalid Dragonpay callback request: %s', self.form.errors)

            if not self.allow_invalid_data:
                raise Exception('Invalid Dragonpay request')

        if self.request.method == 'GET' and not self.update_on_GET:
            # skip transaction updates if its a GET request
            pass

        elif settings.DRAGONPAY_SAVE_DATA:
            try:
                txn = DragonpayTransaction.objects.get(
                    id=self.form.cleaned_data['txnid'])
            except DragonpayTransaction.DoesNotExist as e:
                if not self.allow_invalid_data:
                    raise e
            else:
                # update the status of the transaction
                txn.status = self.form.cleaned_data['status']

                # set the reference number if it is still null
                if not txn.refno:
                    txn.refno = self.form.cleaned_data['refno']

                txn.save(update_fields=['status', 'refno'])
                logger.debug(
                    'Transaction %s updated to %s', txn.id, txn.status)
        return super(
            DragonpayCallbackBaseHandler, self).dispatch(*args, **kwargs)


class DragonpayPayoutBaseHandler(generic.View):
    allow_invalid_data = True    # should we crash if the data is invalid?

    def dispatch(self, request, *args, **kwargs):
        self.form = DragonpayPayoutCallbackForm(request.GET)

        if not self.form.is_valid():
            logger.error(
                'Invalid Dragonpay callback request: %s', self.form.errors)
            if not self.allow_invalid_data:
                raise Exception('Invalid Dragonpay request')

        if settings.DRAGONPAY_SAVE_DATA:
            try:
                txn = DragonpayPayout.objects.get(
                    id=self.form.cleaned_data['merchanttxnid'])
            except Exception as e:
                if not self.allow_invalid_data:
                    raise e
            else:
                txn.status = self.form.cleaned_data['status']
                txn.refno = self.form.cleaned_data['refno']

                txn.save(update_fields=['status', 'refno'])

                logger.debug('Payout %s updated to %s', txn.id, txn.status)
        return super(
            DragonpayPayoutBaseHandler, self).dispatch(
                request, *args, **kwargs)
