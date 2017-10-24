import datetime

from evosnap import constants
from evosnap.transactions.enum import ChargeType


class Capture:
    def __init__(self, transaction_id, amount=None, tip_amount=None, addendum=None):
        """
        Cardholder address data for Address Verification System (AVS). This element is Optional.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['$type', 'Amount', 'TransactionId', 'TipAmount', 'Addendum']
        self.i_type='BankcardCapture,http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard'
        self.amount=amount or '0.00'
        self.addendum=addendum
        self.tip_amount=tip_amount or '0.00'
        self.transaction_id=transaction_id