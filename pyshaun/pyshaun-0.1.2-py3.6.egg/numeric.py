__all__ = ['Numeric']

class Numeric(object):
    def __init__(self, value, unit=None):
        self.value = value
        self.unit = unit

    def __float__(self):
        return self.value

    def __int__(self):
        return int(self.value)

    def __str__(self):
        ret = str(self.value)
        if self.unit is not None:
            ret = ret + self.unit
        return ret

    def __repr__(self):
        return str(self)
