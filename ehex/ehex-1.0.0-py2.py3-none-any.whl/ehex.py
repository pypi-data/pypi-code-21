'''ehex.py'''


class ehex(object):
    '''
    Implements Traveller eHex
    - Assign value: p = ehex(6)
    - Declare without value => value = 0
      p = ehex() => int(p) == 0, str(p) == '0'
    - int(p) returns int representation
    - str(p) returns str representation
    - You can compare with either str or int
    - add: int or str or ehex to ehex
        return result as ehex
        raise ValueError if result falls outside valid
    - subtract: int or str or ehex from ehex
        return result as ehex
        raise ValueError if resullt falls outside valid
    '''
    def __init__(self, value=0):
        self.valid = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        if isinstance(value, str):
            if self.valid.find(value) != -1:
                self._value = self.valid.find(value)
            else:
                raise ValueError('Invalid value {}'.format(value))
        elif isinstance(value, int):
            if value < len(self.valid) and value >= 0:
                self._value = value
            else:
                raise ValueError('Invalid value {}'.format(value))
        elif isinstance(value, ehex):
            self._value = int(value)
        else:
            raise TypeError(
                '%s %s should be int or str', type(value), value)

    def __int__(self):
        return self._value

    def __index__(self):
        return self.__int__()

    def __str__(self):
        return self.valid[self._value]

    def __repr__(self):
        return self.valid[self._value]

    def __eq__(self, other):
        if isinstance(other, str):
            return self.valid[self._value] == other
        elif isinstance(other, int):
            return self._value == other
        elif isinstance(other, ehex):
            return self._value == int(other)
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __ne__(self, other):
        if isinstance(other, str):
            return self.valid[self._value] != other
        elif isinstance(other, int):
            return self._value != other
        elif isinstance(other, ehex):
            return self._value != int(other)
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __lt__(self, other):
        if isinstance(other, str):
            return self.valid[self._value] < other
        elif isinstance(other, int):
            return self._value < other
        elif isinstance(other, ehex):
            return self._value < int(other)
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __gt__(self, other):
        if isinstance(other, str):
            return self.valid[self._value] > other
        elif isinstance(other, int):
            return self._value > other
        elif isinstance(other, ehex):
            return self._value > int(other)
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __le__(self, other):
        if isinstance(other, str):
            return self.valid[self._value] <= other
        elif isinstance(other, int):
            return self._value <= other
        elif isinstance(other, ehex):
            return self._value <= int(other)
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __ge__(self, other):
        if isinstance(other, str):
            return self.valid[self._value] >= other
        elif isinstance(other, int):
            return self._value >= other
        elif isinstance(other, ehex):
            return self._value >= int(other)
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __add__(self, other):
        if isinstance(other, str):
            ehex2 = ehex(other)
            try:
                return ehex(self._value + int(ehex2))
            except ValueError:
                raise
        elif isinstance(other, int):
            try:
                return ehex(self._value + other)
            except ValueError:
                raise
        elif isinstance(other, ehex):
            try:
                return ehex(self._value + int(other))
            except ValueError:
                raise
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __sub__(self, other):
        if isinstance(other, str):
            ehex2 = ehex(other)
            try:
                return ehex(self._value - int(ehex2))
            except ValueError:
                raise
        elif isinstance(other, int):
            try:
                return ehex(self._value - other)
            except ValueError:
                raise
        elif isinstance(other, ehex):
            try:
                return ehex(self._value - int(other))
            except ValueError:
                raise
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)

    def __rsub__(self, other):
        if isinstance(other, str):
            ehex2 = ehex(other)
            try:
                return ehex(int(ehex2) - self._value)
            except ValueError:
                raise
        elif isinstance(other, int):
            try:
                return ehex(other - self._value)
            except ValueError:
                raise
        elif isinstance(other, ehex):
            try:
                return ehex(int(other) - self._value)
            except ValueError:
                raise
        else:
            raise TypeError(
                '%s %s should be ehex, int or str', type(other), other)
