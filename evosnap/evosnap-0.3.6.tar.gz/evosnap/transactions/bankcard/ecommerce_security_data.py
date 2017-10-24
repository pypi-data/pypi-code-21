from evosnap import constants


class EcommerceSecurityData:
    def __init__(self, token_data=None, token_indicator=None, x_i_d=None):
        """
        Ecommerce security elements. This element is Conditional, optional for Ecommerce transactions,
        otherwise not present.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=['TokenData', 'TokenIndicator', 'XID']
        self.token_data=token_data
        self.token_indicator=token_indicator
        self.x_i_d=x_i_d
