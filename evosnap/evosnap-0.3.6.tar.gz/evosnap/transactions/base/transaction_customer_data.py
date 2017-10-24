from evosnap import constants


class TransactionCustomerData:
    def __init__(self, billing_data=None, customer_id=None, customer_tax_id=None,
                 shipping_data=None):
        """
        Contains information about the customer. This element is required by some service providers. If this value is
        set on the transaction and not required by the service provider, the data is not present on the transaction.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['BillingData', 'CustomerId', 'CustomerTaxId',
                      'ShippingData']
        self.billing_data=billing_data
        self.customer_id=customer_id
        self.customer_tax_id=customer_tax_id
        self.shipping_data=shipping_data
