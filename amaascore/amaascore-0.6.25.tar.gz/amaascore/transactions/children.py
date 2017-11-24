from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal

from amaascore.core.amaas_model import AMaaSModel


class Charge(AMaaSModel):

    def __init__(self, charge_value, currency, net_affecting=True, *args, **kwargs):
        self.charge_value = charge_value
        self.currency = currency
        self.net_affecting = net_affecting
        super(Charge, self).__init__(*args, **kwargs)

    @property
    def charge_value(self):
        return self._charge_value

    @charge_value.setter
    def charge_value(self, value):
        """
        Force the charge_value to always be a decimal
        :param value:
        :return:
        """
        self._charge_value = Decimal(value)


class Code(AMaaSModel):

    def __init__(self, code_value, *args, **kwargs):
        self.code_value = code_value
        super(Code, self).__init__(*args, **kwargs)


class Link(AMaaSModel):

    def __init__(self, linked_transaction_id, *args, **kwargs):
        self.linked_transaction_id = linked_transaction_id
        super(Link, self).__init__(*args, **kwargs)


class Party(AMaaSModel):

    def __init__(self, party_id, *args, **kwargs):
        self.party_id = party_id
        super(Party, self).__init__(*args, **kwargs)


class Rate(AMaaSModel):
    
    def __init__(self, rate_value, *args, **kwargs):
        self.rate_value = rate_value
        super(Rate, self).__init__(*args, **kwargs)

    @property
    def rate_value(self):
        return self._rate_value

    @rate_value.setter
    def rate_value(self, value):
        """
        Force the charge_value to always be a decimal
        :param value:
        :return:
        """
        self._rate_value = Decimal(value)
