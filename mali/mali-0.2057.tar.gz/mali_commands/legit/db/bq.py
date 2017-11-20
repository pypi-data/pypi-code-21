# coding=utf-8
import json

from .base_connection import BaseConnection


class BigQueryOperationError(Exception):
    pass


class BigQuerySqlHelper(object):
    @classmethod
    def escape(cls, name):
        return '`%s`' % name

    @classmethod
    def random_function_name(cls):
        return '((FARM_FINGERPRINT(CONCAT(_sha, "$seed")) + POW(2, 63)) / POW(2, 64))'


class BigQueryConnection(BaseConnection):
    @classmethod
    def owner_id_as_org_id(cls, user_id):
        return user_id.replace('-', '_')

    @classmethod
    def _handle_bq_errors(cls, errors):
        if not errors:
            return

        error_msg = json.dumps(errors)

        raise BigQueryOperationError(error_msg)

    def __init__(self, data_volume_config, project, user_id, **kwargs):
        org_name = data_volume_config.org or self.owner_id_as_org_id(user_id)
        self.__table_prefix = data_volume_config.volume_id

        self.__dataset_name = self.__get_dataset_fullname(org_name)
        self.__project = project
        self.__dataset = None
        super(BigQueryConnection, self).__init__(data_volume_config, **kwargs)

    @classmethod
    def __get_dataset_fullname(cls, org_name):
        return 'data_volumes_{org}'.format(org=org_name)

    @property
    def table_prefix(self):
        return self.__table_prefix

    @property
    def project(self):
        return self.__project

    @property
    def dataset(self):
        return self.__dataset_name

    def _create_connection(self, **kwargs):
        from google.cloud import bigquery

        bq_client = bigquery.Client(project=self.__project)
        return bq_client

    def get_table(self, table_ref):
        return self._native_conn.get_table(table_ref)

    def copy_table(self, job_name, destination, *sources):
        return self._native_conn.copy_table(
            job_name, destination, *sources)

    def query(self, query, job_config=None, job_id=None, job_id_prefix=None):
        return self._native_conn.query(query, job_config=job_config, job_id=job_id, job_id_prefix=job_id_prefix)

    def update_table(self, table, properties, retry=None):
        from google.cloud.bigquery import DEFAULT_RETRY

        retry = retry or DEFAULT_RETRY

        return self._native_conn.update_table(table, properties, retry)

    def create_table(self, table):
        return self._native_conn.create_table(table)

    def delete_table(self, table):
        return self._native_conn.delete_table(table)

    def create_rows(self, table, rows, selected_fields=None, **kwargs):
        errors = self._native_conn.create_rows(table, rows, selected_fields=selected_fields, **kwargs)
        self._handle_bq_errors(errors)

    def list_rows(
            self, table, selected_fields=None, max_results=None,
            page_token=None, start_index=None, retry=None):

        from google.cloud.bigquery import DEFAULT_RETRY

        retry = retry or DEFAULT_RETRY
        return self._native_conn.list_rows(table, selected_fields, max_results, page_token, start_index, retry)

    def _create_cursor(self):
        import google.cloud.exceptions
        from google.cloud.bigquery import Dataset

        if self.__dataset is None:
            bq_client = self._native_conn

            dataset_ref = bq_client.dataset(self.__dataset_name)
            dataset = Dataset(dataset_ref)

            if not self.read_only:
                try:
                    bq_client.create_dataset(dataset)
                except google.cloud.exceptions.Conflict:
                    pass

            self.__dataset = dataset

        return self.__dataset

    def _commit(self):
        pass

    def _rollback(self):
        pass

    def create_sql_helper(self):
        return BigQuerySqlHelper()

    def delete_all(self):
        import google.cloud.exceptions

        bq_client = self._native_conn
        dataset_ref = bq_client.dataset(self.__dataset_name)
        try:
            bq_client.delete_dataset(dataset_ref)
        except google.cloud.exceptions.NotFound:
            pass
