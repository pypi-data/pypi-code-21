import datetime

from evosnap import constants


class ReturnById:
    def __init__(self, transaction_id, amount=None, addendum=None, transaction_date_time=None):
        """
        Contains information for returning Bankcard transactions (Credit and PIN Debit).
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['$type', 'TransactionId', 'Amount', 'Addendum', 'TransactionDateTime']
        self.i_type='BankcardReturn,http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard'
        self.amount=amount
        self.addendum=addendum
        self.transaction_date_time=transaction_date_time or datetime.datetime.now().isoformat()
        # self.transaction_data=transaction_data
        self.transaction_id=transaction_id
