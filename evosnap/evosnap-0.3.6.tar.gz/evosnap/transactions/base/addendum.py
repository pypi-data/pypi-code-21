from evosnap import constants


class Addendum:
    def __init__(self, unmanaged=None):
        """
        The Addendum object is used to pass optional service specific information. This object is not required unless
        specifically directed to do so by your EVO Snap* Support team.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.unmanaged=unmanaged
