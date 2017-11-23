class Parameter:
    def __init__(self, base_coin_value, year, month):
        self.base_coin_value = base_coin_value
        self.year = year
        self.month = month

    def year_month_tuple(self):
        return self.year, self.month

    def calculate_base_coin_emission(self, pointz):
        return (self.base_coin_value, round(pointz * self.base_coin_value / 10))


_partners_parameters_dct = {
    1: [Parameter(8, 2016, 1), Parameter(10, 2017, 1), Parameter(20, 2017, 2)],
    2: [Parameter(1, 2016, 1)],
    3: [Parameter(2, 2016, 1)],
    4: [Parameter(3, 2016, 1)],
    5: [Parameter(4, 2016, 1)],
}


class ParameterNotFound(Exception):
    pass


def calculate_base_coin_cost(partner_id, year, month, pointz):
    partner_parameters = _partners_parameters_dct[partner_id]
    for parameter in reversed(partner_parameters):
        if (year, month) >= parameter.year_month_tuple():
            return parameter.calculate_base_coin_emission(pointz)
    raise ParameterNotFound(f'Parameter not found for partner_id {partner_id} on {month}/{year}')
