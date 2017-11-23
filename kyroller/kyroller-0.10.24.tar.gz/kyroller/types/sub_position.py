from .types import *
import json


class SubPosition:
    '''
        持仓
    '''

    def __str__(self):
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)

    def __eq__(self, other):
        return other is not None and self.symbol == other.symbol and self.volume == other.volume

    def __init__(self, symbol, volume, price=0):
        self._symbol = symbol
        self._volume = volume
        self._price = self._cost_price = float(price)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def cost(self):
        return self._cost_price * self._volume

    @property
    def market_value(self):
        return self._price * self._volume

    @property
    def exchange(self)->Exchange:
        if self._symbol[0:2] == 'sh':
            return Exchange.SH
        elif self._symbol[0:2] == 'sz':
            return Exchange.SZ

    @property
    def symbol(self):
        return self._symbol

    @property
    def volume(self):
        return self._volume
