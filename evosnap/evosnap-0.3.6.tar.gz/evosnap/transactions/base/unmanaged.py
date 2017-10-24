from evosnap import constants


class Unmanaged:
    def __init__(self, any):
        """
        Can be used to pass service-specific information such as username/password or session token credentials.
        This element is Optional.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.any=any
