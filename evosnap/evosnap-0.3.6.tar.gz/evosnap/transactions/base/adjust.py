from evosnap import constants


class Adjust:
    def __init__(self, addendum, amount, tip_amount=None, transaction_id=None):
        """
        Contains address information for either the merchant or customer. This element is Optional.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['Addendum', 'Amount', 'TipAmount', 'TransactionId']
        self.addendum=addendum
        self.amount=amount
        self.tip_amount=tip_amount
        self.transaction_id=transaction_id
