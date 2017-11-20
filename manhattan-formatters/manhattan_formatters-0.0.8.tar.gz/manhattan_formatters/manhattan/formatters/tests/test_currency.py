from manhattan import formatters

def test_price():
    """Format an integer as a price"""

    # Check default format is correct
    assert formatters.currency.price(200) == '£2.00'
    assert formatters.currency.price(200000) == '£2,000.00'

    # Check user defined symbol
    assert formatters.currency.price(200, '$') == '$2.00'

    # Check user defined unit conversion
    assert formatters.currency.price(200, '$', 1) == '$200.00'