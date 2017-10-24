from evosnap import constants


class CardData:
    def __init__(self, card_type, p_a_n, cardholder_name=None, expire=None, track1_data=None, track2_data=None):
        """
        Contains information about the payment card. Conditional, required for Authorize and AuthorizeAndCapture
        transactions. May be required for undoing PIN Debit transactions.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['CardType', 'PAN', 'CardholderName', 'Expire', 'Track1Data', 'Track2Data']
        self.cardholder_name=cardholder_name
        self.card_type=card_type
        self.expire=expire
        self.p_a_n=p_a_n
        self.track1_data=track1_data
        self.track2_data=track2_data
