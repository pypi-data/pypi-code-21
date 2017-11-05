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
        self.__create_tree_cache(connection)
        self.__delete_temp_on_commit = delete_temp_on_commit
        super(BigQueryMLIndex, self).__init__(connection)

    def __create_tree_cache(self, connection):
        if GAEDatastoreTreeCache is not None:
            datastore_connection = GAEDatastoreConnection(connection.data_volume_config)
        else:
            datastore_connection = DatastoreConnection(connection.data_volume_config, connection.project)

        tree_cache_class = GAEDatastoreTreeCache if GAEDatastoreTreeCache is not None else DatastoreTreeCache
        self.__tree_cache = tree_cache_class(datastore_connection)

    def __get_index_table_name(self, name):
        table_full_name = '{prefix}_{name}'.format(prefix=self._connection.table_prefix, name=name)

        return table_full_name

    def __get_index_table(self):
        return self._get_table(self.INDEX_TABLE_NAME, schema=self.__table_schema())

    def __get_staging_index_table(self):
        staging_table_name = '%s_%s' % (self.STAGING_INDEX_TABLE_NAME, self.__version)
        return self._get_table(staging_table_name, schema=self.__table_schema())

    def staging_count_items(self, with_metadata=False):
        staging_table = self.__get_staging_index_table()
        staging_index_table_full_name = staging_table.name

        with self._connection.get_cursor() as bq_dataset:
            query = """
                SELECT EXACT_COUNT_DISTINCT(name)
                FROM [{dataset_name}.{index_table_name}]
                """.format(
                    dataset_name=bq_dataset.name,
                    index_table_name=staging_index_table_full_name)

            if not with_metadata:
                query += " WHERE RIGHT(name, 9) != '.metadata'"

            results, _ = self._query_sync(query, use_legacy_sql=True)

            return list(results)[0][0]

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
        import google.api.core.exceptions

        def create_table(method):
            index_table = method()

            try:
                index_table.patch(schema=index_table.schema)
            except google.api.core.exceptions.NotFound:
                try:
                    index_table.create()
                except google.api.core.exceptions.Conflict as ex:
                    pass

            return index_table

        create_table(self.__get_index_table)
        create_table(self.__get_staging_index_table)

    def set_entries(self, entries):
        if not entries:
            return

        now = datetime.datetime.utcnow()

        rows = [row + (now, ) for row in self._decode_entries(entries)]

        logging.debug('inserting %s rows into bq', len(rows))

        table = self.__get_staging_index_table()
        self.__tree_cache.set_entries(entries)
        self.handle_bq_errors(table.insert_data(rows))

        logging.debug('inserted %s rows into bq', len(rows))

    def get_commit_id(self):
        return self.__tree_cache.get_commit_id()

    def __truncate_staging(self):
        if not self.__delete_temp_on_commit:
            logging.debug('index: delete_temp_on_commit: False')
            return

        logging.info('truncate index staging')

        staging_table = self.__get_staging_index_table()
        staging_table.delete()

    def begin_commit(self, tree_id):
        bq_client = self._connection

        staging_table = self.__get_staging_index_table()
        index_table = self.__get_index_table()

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
                dataset_name=bq_dataset.name,
                staging_table_name=staging_table.name,
                index_table_name=index_table.name,
            )

            src_query_parameters = ()

            self._copy_table_data(
                src_query, src_query_parameters, self.__get_index_table())

    def end_commit(self):
        self.__truncate_staging()
