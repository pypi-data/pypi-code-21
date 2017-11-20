__all__ = [
    'price'
    ]


def price(amount, symbol='£',  unit_conversion=100):
    """
    Format the given amount as a price, e.g: `'£12.50'`

    Optionally a unit conversion can be specified, the default `100` e.g pence
    to pounds, cents to dollars, etc.

    Optionally a symbol can be specified (e.g `'$'`), we default to the `'£'`.

    NOTE: It is assumed that the price is an integer and not a float or decimal.
    """
    return '{symbol}{amount:,.2f}'.format(
        amount=float(amount) / unit_conversion,
        symbol=symbol
        )