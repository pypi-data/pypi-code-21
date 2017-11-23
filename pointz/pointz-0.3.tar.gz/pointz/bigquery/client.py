from google.cloud.bigquery.client import Client

from pointz import settings

client = Client.from_service_account_json(settings.BIGQUERY_SECRET_JSON)

dataset_pointz = client.dataset('pointz')
