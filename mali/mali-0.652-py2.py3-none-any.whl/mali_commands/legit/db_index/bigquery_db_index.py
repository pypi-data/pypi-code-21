# coding=utf-8
from ..bigquery_mixin import BigQueryMixin
from .base_db_index import BaseMLIndex
from .cache import DatastoreTreeCache, GAEDatastoreTreeCache
from ..db import DatastoreConnection, GAEDatastoreConnection


# noinspection SqlNoDataSourceInspection,SqlResolve
class BigQueryMLIndex(BaseMLIndex, BigQueryMixin):
    STAGING_INDEX_TABLE_NAME = 'staging_index'
    INDEX_TABLE_NAME = 'index'

    def __init__(self, connection):
        self.__index_table = None

        self.__create_tree_cache(connection)
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

    def __get_table(self, bq_dataset, name):
        index_table_full_name = self.__get_index_table_name(name)

        return bq_dataset.table(index_table_full_name, schema=self.__table_schema())

    def __get_index_table(self, bq_dataset):
        return self.__get_table(bq_dataset, self.INDEX_TABLE_NAME)

    def __get_staging_index_table(self, bq_dataset):
        return self.__get_table(bq_dataset, self.STAGING_INDEX_TABLE_NAME)

    def count_items(self, with_metadata=False):
        staging_index_table_full_name = self.__get_index_table_name(self.STAGING_INDEX_TABLE_NAME)

        with self._connection.get_cursor() as bq_dataset:
            query = 'SELECT EXACT_COUNT_DISTINCT(name) FROM [{dataset_name}.{index_table_name}]'.format(
                dataset_name=bq_dataset.name,
                index_table_name=staging_index_table_full_name)

            results = list(self._query_sync(query, use_legacy_sql=True))

            return results[0][0]

    @classmethod
    def __table_schema(cls):
        from google.cloud import bigquery

        schema = (
            bigquery.SchemaField('name', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('ctime', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('mtime', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('mode', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('uid', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('gid', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('size', 'INTEGER', 'REQUIRED'),
        )

        return schema

    def _create_table_if_needed(self):
        import google.api.core.exceptions

        with self._connection.get_cursor() as bq_dataset:
            def create_table(method):
                index_table = method(bq_dataset)

                try:
                    index_table.create()
                except google.api.core.exceptions.Conflict:
                    pass

                return index_table

            self.__index_table = create_table(self.__get_index_table)
            self.__staging_index_table = create_table(self.__get_staging_index_table)

    def set_entries(self, entries):
        if not entries:
            return

        rows = self._decode_entries(entries)

        with self._connection.get_cursor() as bq_dataset:
            table = self.__get_staging_index_table(bq_dataset)

            self.__tree_cache.set_entries(entries)

            table.insert_data(rows)

    def get_commit_id(self):
        return self.__tree_cache.get_commit_id()

    def commit(self):
        raise NotImplementedError(self.commit)
