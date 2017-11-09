__version__ = '1.0.0'

from random import randint
from functools import wraps


def _digit_validator(fun):
    @wraps(fun)
    def digit_wrapper(*args, **kwargs):
        for arg in args:
            if not str(arg).isdigit():
                raise ValueError('The given argument must be a string a digits')
        return fun(*args, **kwargs)
    return digit_wrapper


@_digit_validator
def _checksum(string):
    """Calculates the luhn checksum of the given string of digits."""
    doubled = [int(n)*2 if i % 2 != 0 else int(n) for i, n in enumerate(string[::-1])]
    return sum(map(lambda n: (n % 10 + 1) if n > 9 else n, doubled)) % 10


def rand(length=16):
    """Create a random valid luhn string of digits"""
    if length < 1:
        raise ValueError('The `length` attribute must be greater than 1')

    ran_str = ''.join(([str(randint(1, 9))] + [str(randint(0, 9)) for _ in range(length-2)]))
    return '{}{}'.format(ran_str, digit(ran_str))


@_digit_validator
def verify(string):
    """Check if the provided string complies with the Luhn Algorithm"""
    return _checksum(string) % 10 == 0


@_digit_validator
def digit(string):
    """Generate the luhn check digit for the provided string of digits"""
    return (10 - _checksum(string + '0')) % 10


@_digit_validator
def complete(string):
    """Append the luhn check digit to the provided string of digits"""
    return '{}{}'.format(string, digit(string))
