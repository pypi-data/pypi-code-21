from datetime import datetime
from decimal import Decimal

from pointz.bigquery.uploader import sql_transaction_to_bigquery_row
from pointz.db.constants import GAS
from pointz.db.schema import Transaction, Partner, Region, Subsidiary


def test_sql_transaction_to_bigquery_row():
    partner = Partner(name='Posto Flex', id=1, segment=GAS)
    region = Region(id=2, name='Fortaleza', partner=partner)
    subsidiary = Subsidiary(id=3, name='Posto 1', region=region)
    transaction = Transaction(
        id=4,
        subsidiary=subsidiary,
        sale=Decimal('1.99'),
        pointz_sale=Decimal('3.45'),
        pointz=5,
        creation=datetime(2017, 6, 7, 8, 9, 10)

    )
    row = sql_transaction_to_bigquery_row(transaction)
    assert (4, 199, 345, 5, 2017, 6, 7, 'Posto 1', 3, 'Fortaleza', 2, 'Posto Flex', 1, GAS) == row
