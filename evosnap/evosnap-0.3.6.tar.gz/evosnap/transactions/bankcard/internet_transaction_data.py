from evosnap import constants


class InternetTransactionData:
    def __init__(self, ip_address=None, session_id=None):
        """
        Contains information about the internet connection. This element is required by some service providers.
        If this value is set on the transaction and not required by the service provider, the data is not
        present on the transaction.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['IpAddress', 'SessionId']
        self.ip_address=ip_address
        self.session_id=session_id
