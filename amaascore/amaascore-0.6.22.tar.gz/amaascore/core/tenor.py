from __future__ import absolute_import, division, print_function, unicode_literals

from dateutil.relativedelta import relativedelta


class Tenor(object):

    def __init__(self, tenor=None):
        if not self.check_tenor(tenor):
            raise ValueError("Invalid tenor: %s" % tenor)
        self.tenor = tenor

    @staticmethod
    def valid_tenors():
        return ['1M', '3M', '6M', '9M', '1Y', '2Y', '5Y', '10Y', '15Y', '20Y', '30Y', '40Y', '50Y']

    @classmethod
    def check_tenor(cls, tenor):
        return tenor in cls.valid_tenors()

    @classmethod
    def tenor_to_relativedelta(cls, tenor):
        if not cls.check_tenor(tenor):
            raise ValueError("Invalid tenor: %s" % tenor)
        tenor_mapping = {'M': 'months', 'Y': 'years'}
        time_quantity = int(tenor[:-1])
        time_attribute = tenor_mapping.get(tenor[-1])
        relative_delta_attribute = {time_attribute: time_quantity}
        return relativedelta(**relative_delta_attribute)

    def to_relativedelta(self):
        return self.tenor_to_relativedelta(self.tenor)
