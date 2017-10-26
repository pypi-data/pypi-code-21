from fractions import Fraction, gcd
import math

class ComplexFraction(object):
    def __init__(self, frac, is_imag=False):
        self.frac = Fraction(frac)
        self.is_imag = is_imag

    def

    __radd__ = __add__
    __rmul__ = __mul__

    def __str__(self):
        return "(" + str(self.numerator) + ")/" + str(self.denominator)

    __repr__ = __str__
