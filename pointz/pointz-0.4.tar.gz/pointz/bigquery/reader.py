from datetime import date

from google.cloud import bigquery

from pointz.bigquery.client import client

ANNUAL_DRE_QUERY = """
SELECT
  SUM(sale + pointz_sale) AS sales,
  SUM(pointz_sale) AS pointz_sales,
  SUM(pointz) as pointz,
  year,
  month,
  region_name,
  partner_name,
  segment_name,
  partner_id
FROM
  `pointz.transactions`
WHERE
  year = @year
GROUP BY
  segment_name,
  partner_name,
  region_name,
  month,
  year,
  partner_id
ORDER BY
  segment_name,
  partner_name,
  region_name,
  year,
  month
"""

MAX_ID_QUERY = 'SELECT MAX(id) as max_id FROM `pointz.transactions`'


def get_annual_dre_by_partner_region(year=None):
    if year is None:
        year = date.today().year
    year = int(year)
    year_param = bigquery.ScalarQueryParameter('year', 'INT64', year)
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = [year_param]
    query_job = client.query(
        ANNUAL_DRE_QUERY, job_config=job_config)  # API request - starts the query

    # Waits for the query to finish
    return query_job.result()


def get_max_transaction_id():
    job_config = bigquery.QueryJobConfig()
    query_job = client.query(MAX_ID_QUERY, job_config=job_config)

    # Waits for the query to finish
    return list(query_job.result())[0].max_id


if __name__ == '__main__':
    annual_reports = get_annual_dre_by_partner_region()
    lst = list(annual_reports)
    print(lst)
