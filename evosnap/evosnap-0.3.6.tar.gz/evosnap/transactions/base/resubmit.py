from evosnap import constants
from evosnap.transactions.enum import UndoReason, PINDebitUndoReason


class Resubmit:
    def __init__(self, transaction_id, addendum=None, payment_authorization_response=None, c_v_v=None):
        """
        Contains information for resubmitting a transaction. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['$type', 'PaymentAuthorizationResponse', 'Addendum', 'CVV', 'TransactionId']
        self.i_type='Resubmit3DSecure, http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard'
        self.payment_authorization_response = payment_authorization_response
        self.addendum=addendum
        self.c_v_v= c_v_v
        self.transaction_id=transaction_id
