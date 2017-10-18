from evosnap import constants
from evosnap.transactions.enum import TransactionType


class Transaction:
    def __init__(self, transaction_type, tender_data, transaction_data, addendum=None, customer_data=None, reporting_data=None,
                 application_configuration_data=None):
        """
        Contains all information required to send a transaction to a service provider. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['$type','Addendum', 'CustomerData', 'ReportingData', 'TenderData', 'TransactionData',
                          'ApplicationConfigurationData']

        if not isinstance(transaction_type, TransactionType):
            raise TypeError('transaction_type must be an instance of TransactionType')

        self.i_type=transaction_type
        self.addendum=addendum
        self.customer_data=customer_data
        self.reporting_data=reporting_data
        self.tender_data=tender_data
        self.transaction_data=transaction_data
        self.application_configuration_data=application_configuration_data
