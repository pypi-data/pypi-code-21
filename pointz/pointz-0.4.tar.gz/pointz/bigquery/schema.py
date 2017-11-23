from google.api_core.exceptions import NotFound
from google.cloud.bigquery import Table, SchemaField

from pointz.bigquery.client import client, dataset_pointz



print(dataset_pointz)

_transactions_ref = dataset_pointz.table('transactions')
try:
    transactions_table = client.get_table(_transactions_ref)
except NotFound:
    transactions_table = Table(_transactions_ref)
    _schema = [
        SchemaField('id', 'INT64', 'REQUIRED', None),
        SchemaField('sale', 'INT64', 'REQUIRED', None),
        SchemaField('pointz_sale', 'INT64', 'REQUIRED', None),
        SchemaField('pointz', 'INT64', 'REQUIRED', None),
        SchemaField('year', 'INT64', 'REQUIRED', None),
        SchemaField('month', 'INT64', 'REQUIRED', None),
        SchemaField('day', 'INT64', 'REQUIRED', None),
        SchemaField('store_name', 'string', 'REQUIRED', None),
        SchemaField('store_id', 'INT64', 'REQUIRED', None),
        SchemaField('region_name', 'string', 'REQUIRED', None),
        SchemaField('region_id', 'INT64', 'REQUIRED', None),
        SchemaField('partner_name', 'string', 'REQUIRED', None),
        SchemaField('partner_id', 'INT64', 'REQUIRED', None),
        SchemaField('segment_name', 'string', 'REQUIRED', None),
    ]

    transactions_table.schema = _schema
    transactions_table = client.create_table(transactions_table)

