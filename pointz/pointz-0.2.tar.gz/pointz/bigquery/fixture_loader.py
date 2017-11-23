from os import path

from google.cloud import bigquery

from pointz.bigquery.client import client, dataset_pointz

_json_file_path = path.dirname(__file__)
_json_file_path = path.join('fixtures', 'transactions.csv')

table_ref = dataset_pointz.table('transactions')
job_config = bigquery.LoadJobConfig()
job_config.skip_leading_rows = 1
with open(_json_file_path, 'rb') as file:
    job = client.load_table_from_file(
        file, table_ref, job_config=job_config)  # API request
    job.result()  # Waits for table load to complete.