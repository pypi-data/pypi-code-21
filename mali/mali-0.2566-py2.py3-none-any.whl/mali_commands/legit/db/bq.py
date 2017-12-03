# -*- coding: utf8 -*-
import json
import logging
import time

from .base_connection import BaseConnection


class BigQueryOperationError(Exception):
    pass


class BigQuerySqlHelper(object):
    @classmethod
    def escape(cls, name):
        return '`%s`' % name

    @classmethod
    def random_function_name(cls):
        return '((FARM_FINGERPRINT($field_random_generator) + POW(2, 63)) / POW(2, 64))'


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
        return _bq_retry(self._native_conn.create_table, table)

    def delete_table(self, table):
        import google.cloud.exceptions
        try:
            self._native_conn.delete_table(table)
        except google.cloud.exceptions.NotFound:
            logging.info("Table '%s' is not found" % table.table_id)

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
                    _bq_retry(bq_client.create_dataset, dataset)
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

    def delete_tables(self, prefixes=None):
        import google.cloud.exceptions

        if not prefixes:
            prefixes = ['']
        elif not isinstance(prefixes, (list, tuple)):
            prefixes = [prefixes]

        logging.info("delete table with prefixes = '%s' in dataset '%s'" % (prefixes, self.__dataset_name))

        bq_client = self._native_conn
        dataset_ref = bq_client.dataset(self.__dataset_name)

        try:
            for table_ref in bq_client.list_dataset_tables(dataset_ref):
                for prefix in prefixes:
                    if not table_ref.table_id.startswith(prefix):
                        continue

                    self.delete_table(table_ref)
        except google.cloud.exceptions.NotFound:
            # This will catch list_dataset_tables errors when the dataset is not found
            pass


INITIAL_DELAY = 1.0
MAXIMUM_DELAY = 10.0
DELAY_MULTIPLIER = 2.0


def _bq_retry(method, *args, **kwargs):
    from google.api_core.exceptions import GoogleAPICallError

    delay = 1.0
    while True:
        try:
            return method(*args, **kwargs)
        except GoogleAPICallError as ex:
            logging.info('run %s with exception %s', method.__name__, ex)
            if not _should_retry(ex):
                raise

        delay = min(delay * 2, 10)
        time.sleep(delay)


def _should_retry(ex):
    if len(ex.errors) == 0:
        return False

    reason = ex.errors[0]['reason']
    return reason in ['backendError', 'rateLimitExceeded', 'internalError']
