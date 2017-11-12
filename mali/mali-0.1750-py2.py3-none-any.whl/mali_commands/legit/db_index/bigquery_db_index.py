# coding=utf-8
import datetime
import logging

from ..bigquery_mixin import BigQueryMixin
from .base_db_index import BaseMLIndex
from .cache import DatastoreTreeCache, GAEDatastoreTreeCache
from ..db import DatastoreConnection, GAEDatastoreConnection


# noinspection SqlNoDataSourceInspection,SqlResolve
class BigQueryMLIndex(BaseMLIndex, BigQueryMixin):
    STAGING_INDEX_TABLE_NAME = 'staging_index'
    INDEX_TABLE_NAME = 'index'

    def __init__(self, connection, version=None, delete_temp_on_commit=True):
        self.__version = version or 0

        super(BigQueryMLIndex, self).__init__(connection)
        self.__delete_temp_on_commit = delete_temp_on_commit
        self.__create_tree_cache(connection)

    def __create_tree_cache(self, connection):
        if GAEDatastoreTreeCache is not None:
            org_id = self._connection.data_volume_config.org
            volume_id = self._connection.data_volume_config.volume_id

            tree_cache = GAEDatastoreTreeCache(org_id, volume_id)
        else:
            datastore_connection = DatastoreConnection(connection.data_volume_config, connection.project)
            tree_cache = DatastoreTreeCache(datastore_connection)

        self.__tree_cache = tree_cache

    def __get_index_table_ref(self):
        return self._get_table_ref(self.INDEX_TABLE_NAME)

    def __get_staging_index_table_ref(self):
        staging_table_name = '%s_%s' % (self.STAGING_INDEX_TABLE_NAME, self.__version)
        return self._get_table_ref(staging_table_name)

    def __query_count_metadata_and_data_point(self, query):
        from google.cloud.bigquery import QueryJobConfig

        job_config = QueryJobConfig()

        job = self._query_async(query, job_config)
        rows_iter = list(job.result())

        result = {}
        for row in rows_iter:
            field = 'total_meta_data' if row[0] else 'total_data_points'
            result[field] = row[1]

        return result.get('total_data_points', 0), result.get('total_meta_data', 0)

    def version_count_items(self):
        with self._connection.get_cursor() as bq_dataset:
            query = """
                #standardSQL
                SELECT ANY_VALUE(ENDS_WITH(name, '.metadata')), COUNT(DISTINCT name) 
                FROM (SELECT DISTINCT name
                  FROM `{dataset_name}.{index_table_name}`
                  UNION ALL
                    SELECT DISTINCT name
                    FROM `{dataset_name}.{staging_index_table_name}`
                )
                GROUP BY ENDS_WITH(name, '.metadata')
                """.format(
                    dataset_name=bq_dataset.dataset_id,
                    staging_index_table_name=self.__get_staging_index_table_ref().table_id,
                    index_table_name=self.__get_index_table_ref().table_id
            )

            return self.__query_count_metadata_and_data_point(query)

    def staging_count_items(self):
        staging_table_ref = self.__get_staging_index_table_ref()
        staging_index_table_full_name = staging_table_ref.table_id

        with self._connection.get_cursor() as bq_dataset:
            query = """
                #standardSQL
                SELECT ANY_VALUE(ENDS_WITH(name, '.metadata')), COUNT(DISTINCT name)
                FROM {dataset_name}.{index_table_name}
                GROUP BY ENDS_WITH(name, '.metadata')
                """.format(
                    dataset_name=bq_dataset.dataset_id,
                    index_table_name=staging_index_table_full_name)

            return self.__query_count_metadata_and_data_point(query)

    @classmethod
    def __table_schema(cls):
        from google.cloud import bigquery

        schema = (
            bigquery.SchemaField('name', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('ctime', 'FLOAT', 'REQUIRED'),
            bigquery.SchemaField('mtime', 'FLOAT', 'REQUIRED'),
            bigquery.SchemaField('mode', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('uid', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('gid', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('size', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('url', 'STRING'),
            bigquery.SchemaField('ts', 'TIMESTAMP', 'REQUIRED'),  # this has to be the last column
        )

        return schema

    def _create_table_if_needed(self):
        import google.cloud.exceptions
        from google.cloud.bigquery.table import Table

        bq_client = self._connection

        def create_table(method):
            index_table_ref = method()

            table = Table(index_table_ref)
            table.schema = self.__table_schema()

            try:
                bq_client.update_table(table, ['schema'])
            except google.cloud.exceptions.NotFound:
                try:
                    bq_client.create_table(table)
                except google.cloud.exceptions.Conflict:
                    pass

            return table

        create_table(self.__get_index_table_ref)
        create_table(self.__get_staging_index_table_ref)

    def set_entries(self, entries):
        if not entries:
            return

        now = datetime.datetime.utcnow()

        rows = [row + (now, ) for row in self._decode_entries(entries)]

        logging.debug('inserting %s rows into bq', len(rows))

        index_table_ref = self.__get_staging_index_table_ref()

        bq_client = self._connection

        bq_client.create_rows(index_table_ref, rows, selected_fields=self.__table_schema())

        self.__tree_cache.set_entries(entries)

        logging.debug('inserted %s rows into bq', len(rows))

    def get_commit_id(self):
        return self.__tree_cache.get_commit_id()

    def __truncate_staging(self):
        if not self.__delete_temp_on_commit:
            logging.debug('index: delete_temp_on_commit: False')
            return

        logging.info('truncate index staging')

        staging_table_ref = self.__get_staging_index_table_ref()
        bq_client = self._connection
        bq_client.delete_table(staging_table_ref)

    def begin_commit(self, tree_id):
        bq_client = self._connection

        staging_table_ref = self.__get_staging_index_table_ref()
        index_table_ref = self.__get_index_table_ref()

        with bq_client.get_cursor() as bq_dataset:
            src_query = """
                #standardSQL
                SELECT staging_index_table.*
                FROM (
                    SELECT
                      * EXCEPT(row_number)
                    FROM (
                      SELECT *, ROW_NUMBER() OVER (PARTITION BY name) row_number
                      FROM
                        `{dataset_name}.{staging_table_name}`
                    )
                    WHERE
                      row_number = 1
                ) staging_index_table
                LEFT JOIN `{dataset_name}.{index_table_name}` index_table
                ON staging_index_table.sha = index_table.sha
                WHERE index_table.sha is NULL
              """.format(
                dataset_name=bq_dataset.dataset_id,
                staging_table_name=staging_table_ref.table_id,
                index_table_name=index_table_ref.table_id,
            )

            src_query_parameters = ()

            self._copy_table_data(
                src_query, src_query_parameters, self.__get_index_table_ref())

    def end_commit(self):
        self.__truncate_staging()
