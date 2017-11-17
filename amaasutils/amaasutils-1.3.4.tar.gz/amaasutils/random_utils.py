""" Helper functions for generating random data """
from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from decimal import Decimal
import random
import string


def random_string(length, numeric_only=False):
    """
    Generates a random string of length equal to the length parameter
    """
    choices = string.digits if numeric_only else string.ascii_uppercase + string.digits
    return ''.join(random.choice(choices) for _ in range(length))


def random_decimal():
    """
    Generates a random "sensible" decimal for things like prices
    """
    return Decimal(random.random() * 100).quantize(Decimal('0.01'))


def random_date(start_year=2000, end_year=2020):
    """
    Generates a random "sensible" date for use in things like issue dates and maturities
    """
    return date(random.randint(start_year, end_year), random.randint(1, 12), random.randint(1, 28))
