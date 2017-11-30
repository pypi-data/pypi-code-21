import random
from decimal import Decimal
from typing import Union


# noinspection PyShadowingBuiltins
def decimal(min: Union[int, Decimal], max: Union[int, Decimal]) -> Decimal:
    return Decimal(random.randint(min, max))
