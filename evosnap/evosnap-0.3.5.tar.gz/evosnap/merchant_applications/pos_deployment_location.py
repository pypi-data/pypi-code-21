from evosnap import constants


class POSDeploymentLocation:
    def __init__(self,**kwargs):
        self.__order = [
            'posDLTradeName', 'posDLContactFirstName', 'posDLContactLastName', 'posDLAddress',
            'posDLEmail', 'posDLCity', 'posDLCounty', 'posDLPostalCode',
            'posDLCountry', 'posDLPhone', 'posDLRentalTermID',
            'posDLTerminalArray', 'posDLExistingSENumber',
        ]
        self.__lower_camelcase = constants.ALL_FIELDS

        self.pos_d_l_trade_name = kwargs.get('pos_d_l_trade_name')
        self.pos_d_l_contact_first_name = kwargs.get('pos_d_l_contact_first_name')
        self.pos_d_l_contact_last_name = kwargs.get('pos_d_l_contact_last_name')
        self.pos_d_l_address = kwargs.get('pos_d_l_address')
        self.pos_d_l_email = kwargs.get('pos_d_l_email')
        self.pos_d_l_city = kwargs.get('pos_d_l_city')
        self.pos_d_l_county = kwargs.get('pos_d_l_county')
        self.pos_d_l_postal_code = kwargs.get('pos_d_l_postal_code')
        self.pos_d_l_country = kwargs.get('pos_d_l_country')
        self.pos_d_l_phone = kwargs.get('pos_d_l_phone')
        self.pos_d_l_rental_term_i_d = kwargs.get('pos_d_l_rental_term_i_d')
        self.pos_d_l_terminal_array = kwargs.get('pos_d_l_terminal_array')
        self.pos_d_l_existing_s_e_number = kwargs.get('pos_d_l_existing_s_e_number')

    @property
    def pos_d_l_terminal_array_hash(self):
        return ''.join([f.hash_str for f in self.pos_d_l_terminal_array])

    @property
    def hash_str(self):
        required = [
            'pos_d_l_trade_name', 'pos_d_l_contact_first_name', 'pos_d_l_contact_last_name', 'pos_d_l_address',
            'pos_d_l_email', 'pos_d_l_city', 'pos_d_l_county', 'pos_d_l_postal_code',
            'pos_d_l_country', 'pos_d_l_phone', 'pos_d_l_rental_term_i_d',
            'pos_d_l_terminal_array_hash', 'pos_d_l_existing_s_e_number',
        ]
        return ''.join([str(getattr(self,f)).strip() for f in required if getattr(self,f) is not None])