from decimal import Decimal, ROUND_HALF_UP


def precise_round(num):
    return float(Decimal(str(num)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))