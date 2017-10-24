from evosnap import constants


class InternationalAVSOverride:
    def __init__(self, skip_a_v_s=False, ignore_a_v_s=False, a_v_s_reject_codes=None):
        """
        Cardholder address data for Address Verification System (AVS). This element is Optional.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order = ['SkipAVS', 'IgnoreAVS', 'AVSRejectCodes']
        self.skip_a_v_s=skip_a_v_s
        self.ignore_a_v_s=ignore_a_v_s
        self.a_v_s_reject_codes=a_v_s_reject_codes
