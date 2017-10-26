from fractions import Fraction

class ComplexFraction(object):
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return ComplexFraction(
            self.real + other.real,
            self.imag + other.imag)

    def __mul__(self, other):
        return ComplexFraction(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real)

    def __str__(self):
        return ("(" +
                str(self.real.numerator) +
                "/" +
                str(self.real.denominator) +
                ") + i (" +
                str(self.imag.numerator) +
                "/" +
                str(self.imag.denominator) +
                ")")

    def latex_code(self):
        if self.real == 0 and self.imag == 0:
            return "0"
        if self.real == 0:
            real = ""
        else:
            real = r"\frac{{{}}}{{{}}}".format(
                self.real.numerator,
                self.real.denominator)
        if self.imag == 0:
            imag = ""
        else:
            imag = r"\frac{{{}}}{{{}}}".format(
                self.imag.numerator,
                self.imag.denominator)
        return real + r" + i " + imag

def from_string(self, string):
    print "qwer" + string
    real, imag = string[0:-1].split(") + i (")
    return ComplexFraction(Fraction(real), Fraction(imag))
