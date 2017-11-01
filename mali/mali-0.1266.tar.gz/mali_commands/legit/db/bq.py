# coding=utf-8
from .base_connection import BaseConnection


class BigQuerySqlHelper(object):
    @classmethod
    def escape(cls, name):
        return '`%s`' % name

    @classmethod
    def random_function_name(cls):
        return '(FARM_FINGERPRINT(CONCAT(_sha, "$seed")) / 2 + 0.5)'


class BigQueryConnection(BaseConnection):
    @classmethod
    def owner_id_as_org_id(cls, user_id):
        return user_id.replace('-', '_')

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

    def copy_table(self, job_name, destination, *sources):
        return self._native_conn.copy_table(
            job_name, destination, *sources)

    def run_async_query(self, job_name, query, udf_resources=(), query_parameters=()):
        return self._native_conn.run_async_query(
            job_name, query, udf_resources=udf_resources, query_parameters=query_parameters)

    def _create_cursor(self):
        import google.api.core.exceptions

        if self.__dataset is None:
            dataset = self._native_conn.dataset(self.__dataset_name)

            if not self.read_only:
                try:
                    dataset.create()
                except google.api.core.exceptions.Conflict:
                    pass

            self.__dataset = dataset

        return self.__dataset

    def _commit(self):
        pass

    def _rollback(self):
        pass

    def create_sql_helper(self):
        return BigQuerySqlHelper()
