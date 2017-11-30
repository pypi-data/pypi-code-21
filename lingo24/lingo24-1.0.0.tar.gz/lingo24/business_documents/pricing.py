# -*- coding: utf-8 -*-
from decimal import Decimal


DP2 = Decimal('0.00') # 2 decimal places


class Price(object):
    def __init__(self, currency_code, net, gross):
        self.currency_code = currency_code
        self.net = net
        self.gross = gross

    def __repr__(self):
        return '<Price {} {} net / {} gross>'.format(
            self.currency_code,
            self.net,
            self.gross,
        )

    def __eq__(self, other):
        return all((
            self.currency_code == other.currency_code,
            self.net == other.net,
            self.gross == other.gross,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if self.currency_code != other.currency_code:
            raise ValueError('Cannot add prices with different currencies')
        return Price(
            currency_code=self.currency_code,
            net=(self.net + other.net),
            gross=(self.gross + other.gross),
        )

    def _format_currency(self, value):
        if self.currency_code == 'GBP':
            return u'£{}'.format(value)
        elif self.currency_code == 'USD':
            return u'${}'.format(value)
        elif self.currency_code == 'EUR':
            return u'€{}'.format(value)
        return '{} {}'.format(self.currency_code, value)

    @property
    def tax(self):
        return self.gross - self.net

    @property
    def formatted_net(self):
        return self._format_currency(self.net)

    @property
    def formatted_gross(self):
        return self._format_currency(self.gross)

    @property
    def formatted_tax(self):
        return self._format_currency(self.tax)



class TotalPrice(object):
    def __init__(self, total_with_discount, total_without_discount):
        self.total_with_discount = total_with_discount
        self.total_without_discount = total_without_discount

    def __repr__(self):
        return '<TotalPrice: Without discount {} | With discount {}>'.format(
            self.total_without_discount,
            self.total_with_discount,
        )

    def __eq__(self, other):
        if not isinstance(other, TotalPrice):
            return False
        return all((
            self.total_with_discount == other.total_with_discount,
            self.total_without_discount == other.total_without_discount,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        return TotalPrice(
            total_with_discount=(self.total_with_discount + other.total_with_discount),
            total_without_discount=(self.total_without_discount + other.total_without_discount),
        )


class Charge(object):
    def __init__(self, collection, title, value):
        self.collection = collection
        self.title = title
        self.value = value

    def __repr__(self):
        return '<Charge {}: {}>'.format(self.title, self.value)

    def __eq__(self, other):
        return all((
            self.collection == other.collection,
            self.title == other.title,
            self.value == other.value,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)
