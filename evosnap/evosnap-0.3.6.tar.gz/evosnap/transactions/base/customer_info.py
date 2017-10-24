from evosnap import constants


class CustomerInfo:
    def __init__(self, address=None, business_name=None, email=None,
                 fax=None, name=None, phone=None):
        """
        Contains information about the customer. This element is required by some service providers. If this value is
        set on the transaction and not required by the service provider, the data is not present on the transaction.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['Address', 'BusinessName', 'Email', 'Fax', 'Name', 'Phone']
        self.address=address
        self.business_name=business_name
        self.email=email
        self.fax=fax
        self.name=name
        self.phone=phone
