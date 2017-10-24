from evosnap import constants
from evosnap.transactions.enum import CVDataProvided


class CardSecurityData:
    def __init__(self, international_a_v_s_data=None, c_v_data=None, c_v_data_provided=None, identification_information=None,
                 key_serial_number=None, p_i_n=None, international_a_v_s_override= None):
        """
        Contains security information for the payment card. This element is required for PIN Debit transactions.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['InternationalAVSData', 'InternationalAVSOverride', 'CVData', 'CVDataProvided', 'IdentificationInformation',
                 'KeySerialNumber', 'PIN']
        self.international_a_v_s_data=international_a_v_s_data
        self.international_a_v_s_override=international_a_v_s_override
        self.c_v_data=c_v_data
        if not c_v_data_provided and c_v_data:
            self.c_v_data_provided=CVDataProvided.provided
        elif not c_v_data_provided and not c_v_data:
            self.c_v_data_provided=CVDataProvided.not_set
        else:
            self.c_v_data_provided=c_v_data_provided
        self.identification_information=identification_information
        self.key_serial_number=key_serial_number
        self.p_i_n=p_i_n
