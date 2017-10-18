from evosnap import constants


class InternationalAVSData:
    def __init__(self, cardholder_name=None, street=None, city=None, country=None, email=None, phone=None, postal_code=None,
                 state_province=None, house_number=None):
        """
        Cardholder address data for Address Verification System (AVS). This element is Optional.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order = ['CardholderName', 'Street', 'City', 'Country', 'Email', 'Phone', 'PostalCode',
                 'StateProvince', 'HouseNumber']
        self.cardholder_name=cardholder_name
        self.street=street
        self.city=city
        self.country=country
        self.email=email
        self.phone=phone
        self.postal_code=postal_code
        self.state_province=state_province
        self.house_number=house_number
