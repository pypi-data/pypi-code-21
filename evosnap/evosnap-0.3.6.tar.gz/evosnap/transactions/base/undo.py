from evosnap import constants
from evosnap.transactions.enum import UndoReason, PINDebitUndoReason


class Undo:
    def __init__(self, transaction_id, addendum=None, p_i_n_debit_reason=None, tender_data=None,
                 transaction_code=None, undo_reason=None, force_void=False):
        """
        Contains information for undoing (voiding) a transaction. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['$type', 'PINDebitReason', 'TenderData', 'TransactionId', 'Addendum', 'ForceVoid',
                      'TransactionCode', 'UndoReason']
        self.i_type='BankcardUndo,http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard'
        self.addendum=addendum
        self.transaction_id=transaction_id
        self.p_i_n_debit_reason=p_i_n_debit_reason or PINDebitUndoReason.not_set
        self.tender_data=tender_data
        self.transaction_code=transaction_code or 'NotSet'
        self.undo_reason=undo_reason or UndoReason.customer_cancellation
        self.force_void=force_void
