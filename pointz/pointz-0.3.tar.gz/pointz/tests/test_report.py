import pytest
from google.cloud.bigquery._helpers import Row

from pointz.report import render, Report


def read_report_content():
    columns_dct = {'sales': 0, 'pointz_sales': 1, 'pointz': 2, 'year': 3, 'month': 4, 'region_name': 5,
                   'partner_name': 6,
                   'segment_name': 7, 'partner_id': 8}
    annual_report_result = [
        Row((500, 400, 10, 2017, 1, 'Fortaleza', 'Posto Flex', 'GAS', 1), columns_dct),
        Row((1800, 1600, 40, 2017, 2, 'Fortaleza', 'Posto Flex', 'GAS', 1), columns_dct)
    ]

    report = Report.from_bigquery_result(annual_report_result, 'GAS - Posto Flex - Fortaleza')
    return render('dre.html', report=report)


def test_title():
    report_content = read_report_content()
    assert 'GAS - Posto Flex - Fortaleza' in report_content


@pytest.mark.parametrize('header', ['jan-2017', 'fev-2017'])
def test_month_header(header):
    report_content = read_report_content()
    assert header in report_content


@pytest.mark.parametrize('sale', ['5.00', '18.00', '23.00'])
def test_total_sales(sale):
    report_content = read_report_content()
    assert sale in report_content


@pytest.mark.parametrize('sale', ['4.00', '16.00', '20.00'])
def test_pointz_sales(sale):
    report_content = read_report_content()
    assert sale in report_content


@pytest.mark.parametrize('percentage', ['80%', '89%', '87%'])
def test_sales_percentage(percentage):
    report_content = read_report_content()
    assert percentage in report_content


@pytest.mark.parametrize('value', ['0.010', '0.020'])
def test_base_point_value(value):
    report_content = read_report_content()
    assert value in report_content


@pytest.mark.parametrize('value', ['0.10', '0.80', '0.90'])
def test_base_point_emission(value):
    report_content = read_report_content()
    assert value in report_content
