from evosnap import constants


class TransactionTenderData:
    def __init__(self, encryption_key_id=None, payment_account_data_token=None, secure_payment_account_data=None,
                 swipe_status=None, card_data=None, card_security_data=None, ecommerce_security_data=None):
        """
        Base class object containing information about the tender used for a specific transaction.
        This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['EncryptionKeyId', 'PaymentAccountDataToken', 'SecurePaymentAccountData',
                      'SwipeStatus', 'CardData', 'CardSecurityData', 'EcommerceSecurityData']
        self.encryption_key_id=encryption_key_id
        self.payment_account_data_token=payment_account_data_token
        self.secure_payment_account_data=secure_payment_account_data
        self.swipe_status=swipe_status
        self.card_data=card_data
        self.card_security_data=card_security_data
        self.ecommerce_security_data=ecommerce_security_data
