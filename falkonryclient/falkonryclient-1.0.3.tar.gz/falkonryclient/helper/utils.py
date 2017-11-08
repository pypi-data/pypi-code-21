"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""
import string
import random


def random_string(size=6):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

__all__ = [
    'random_string'
]
