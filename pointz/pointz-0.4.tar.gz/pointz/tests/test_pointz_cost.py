import pytest

from pointz.db.partners_cost import calculate_base_coin_cost


@pytest.mark.parametrize(
    'expected_base_coin_value,expected_base_coin_emission,pointz,partner_id,year,month',
    [
        (10, 10, 10, 1, 2017, 1),
        (20, 80, 40, 1, 2017, 2)
    ]
)
def test_calculate_base_coin_value_varying_on_time(expected_base_coin_value, expected_base_coin_emission, pointz,
                                                   partner_id, year, month):
    assert (expected_base_coin_value, expected_base_coin_emission) == calculate_base_coin_cost(partner_id, year, month,
                                                                                               pointz)
