from decimal import Decimal
from itertools import groupby
from os import path

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader

from pointz.db.partners_cost import calculate_base_coin_cost

_templates_path = path.dirname(__file__)
_templates_path = path.join(_templates_path, 'templates')

_env = Environment(loader=FileSystemLoader(_templates_path))


def _to_str_with_2_digits(dec):
    return f'{dec:.2f}'


_number_to_month_str_dct = {
    1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'
}


class MonthlySummary:
    def __init__(self, month, year, sales, pointz_sales, base_coin_value, base_coin_emission):
        """Class representing a monthly summary dre data

        :param month: month of summary
        :param year: year of summary
        :param sales: total sales in cents
        :param pointz_sales: total sales with pointz in cents
        :param base_coin_value a tenth cent
        """
        self._base_coin_value = Decimal(base_coin_value) / 1000
        self._sales = Decimal(sales) / 100
        self._base_coin_emission = Decimal(base_coin_emission) / 100
        self._pointz_sales = Decimal(pointz_sales) / 100
        self.year = year
        self.month = month

    @property
    def sales(self):
        return _to_str_with_2_digits(self._sales)

    @property
    def pointz_sales(self):
        return _to_str_with_2_digits(self._pointz_sales)

    @property
    def base_coin_emission(self):
        return _to_str_with_2_digits(self._base_coin_emission)

    @property
    def title(self):
        return f'{self.month}-{self.year}'

    @property
    def sales_percentage(self):
        return round(self._pointz_sales * 100 / self._sales)

    @property
    def base_coin_value(self):
        return f'{self._base_coin_value:.3f}'

    @classmethod
    def from_bigquery_row(cls, row):
        month = row.month
        year = row.year
        base_coin_value, base_coin_emission = calculate_base_coin_cost(row.partner_id, year, month, row.pointz)
        month = _number_to_month_str_dct[month]
        summary = cls(month, year, row.sales, row.pointz_sales, base_coin_value, base_coin_emission)
        return summary


class Report:
    def __init__(self, title, monthly_summaries):
        self.monthly_summaries = monthly_summaries
        self.title = title

    @property
    def total_sales(self):
        result = sum(summary._sales for summary in self.monthly_summaries)
        return _to_str_with_2_digits(result)

    @property
    def total_pointz_sales(self):
        result = sum(summary._pointz_sales for summary in self.monthly_summaries)
        return _to_str_with_2_digits(result)

    @property
    def total_base_coin_emission(self):
        result = sum(summary._base_coin_emission for summary in self.monthly_summaries)
        return _to_str_with_2_digits(result)

    @property
    def total_sales_percentage(self):
        result = sum(summary._pointz_sales for summary in self.monthly_summaries) * 100 / sum(
            summary._sales for summary in self.monthly_summaries)
        return round(result)

    @classmethod
    def from_bigquery_result(cls, bigquery_result, title='GAS - Posto Flex - Fortaleza'):
        monthly_summaries = [MonthlySummary.from_bigquery_row(row) for row in bigquery_result]
        return cls(title, monthly_summaries)


def extract_segment_partner_region_title(row):
    return f'{row.segment_name} - {row.partner_name} - {row.region_name}'


def group_region_result(bigquery_result):
    return groupby(bigquery_result, key=extract_segment_partner_region_title)


def render(template, report):
    return _env.get_template(template).render(report=report)


def render_annual_dre_per_partner_region(bigquery_result, title):
    report = Report.from_bigquery_result(bigquery_result, title)
    return render('dre.html', report=report)


def render_multiple_annual_dres(bigquery_result):
    result = []
    for title, annual_group in group_region_result(bigquery_result):
        result.append((title, render_annual_dre_per_partner_region(annual_group, title)))

    return result
