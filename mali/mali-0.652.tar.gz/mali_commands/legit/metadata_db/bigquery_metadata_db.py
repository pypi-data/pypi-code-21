# coding=utf-8
import json
import uuid
import datetime
import os
import six
from base58 import b58encode
from ..bigquery_mixin import BigQueryMixin
from .base_metadata_db import BaseMetadataDB, MetadataTypeNotSupported
from flatten_json import unflatten


# noinspection SqlNoDataSourceInspection
class BigQueryMetadataDB(BaseMetadataDB, BigQueryMixin):
    def get_all_data(self, sha):
        pass

    def get_data_for_commit(self, sha, commit_sha):
        pass

    STAGING_TABLE_NAME = 'staging'
    METADATA_TABLE_NAME = 'metadata'

    def __init__(self, connection):
        self.__staging_table = None
        self.__metadata_table = None
        self.__prev_table_info = None
        super(BigQueryMetadataDB, self).__init__(connection)

    @classmethod
    def __get_table_name(cls, prefix, name):
        table_full_name = '{prefix}_{name}'.format(prefix=prefix, name=name)

        return table_full_name

    def __get_table(self, name):
        table_full_name = self.__get_table_name(self._connection.table_prefix, name)

        with self._connection.get_cursor() as bq_dataset:
            return bq_dataset.table(table_full_name)

    def __create_specific_table(self, name, schema):
        import google.api.core.exceptions

        table = self.__get_table(name)
        table.schema = schema

        try:
            table.create()
        except google.api.core.exceptions.Conflict:
            table.reload()

        return table

    def _create_table(self):
        from google.cloud import bigquery

        schema = (
            bigquery.SchemaField('_sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('_commit_sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('_ts', 'TIMESTAMP'),
        )

        self.__staging_table = self.__create_specific_table(self.STAGING_TABLE_NAME, schema)
        self.__metadata_table = self.__create_specific_table(self.METADATA_TABLE_NAME, schema)

    def __has_column(self, column_name):
        for field in self.__metadata_table.schema:
            if column_name == field.name:
                return True

        return False

    @classmethod
    def __value_to_sql_type(cls, column_value):
        if isinstance(column_value, six.string_types):
            return 'STRING'

        if isinstance(column_value, six.integer_types):
            return 'INTEGER'

        if isinstance(column_value, float):
            return 'FLOAT'

        raise MetadataTypeNotSupported('UNKNOWN TYPE %s' % type(column_value))

    @classmethod
    def bq_field_name_to_common_name(cls, name):
        return '@' + name[1:] if name in ['_commit_sha', '_sha'] else name

    @classmethod
    def common_name_to_bq_field_name(cls, name):
        return '_' + name[1:] if name.startswith('@') else name

    @classmethod
    def _patch_table_with_new_schema(cls, table, schema):
        table.patch(schema=schema)

    def _add_missing_columns(self, data_object):
        from google.cloud import bigquery

        new_columns = []
        for column_name, column_value in data_object.items():
            column_name = self.common_name_to_bq_field_name(column_name)
            if self.__has_column(column_name):
                continue

            new_columns.append(bigquery.SchemaField(column_name, self.__value_to_sql_type(column_value)))

        if len(new_columns) > 0:
            schema = self.__staging_table.schema[:]
            new_columns = sorted(new_columns, key=lambda field: field.name)
            schema.extend(new_columns)
            self._patch_table_with_new_schema(self.__staging_table, schema)
            self._patch_table_with_new_schema(self.__metadata_table, schema)

    def _add_data(self, flatten_data_list):
        rows = []

        now = datetime.datetime.utcnow()

        for flatten_data_list in flatten_data_list:
            row = []
            for field in self.__staging_table.schema:
                common_field_name = self.bq_field_name_to_common_name(field.name)
                if common_field_name == '_ts':
                    row.append(now)
                else:
                    row.append(flatten_data_list[common_field_name])

            rows.append(row)

        self.handle_bq_errors(self.__staging_table.insert_data(rows))

    def __copy_table(self, dest_table, src_table, write_disposition, create_disposition):
        copy_id = str(uuid.uuid4())

        bq_client = self._connection

        copy_job = bq_client.copy_table(copy_id, dest_table, src_table)
        copy_job.write_disposition = write_disposition
        copy_job.create_disposition = create_disposition
        return copy_job

    def commit(self, commit_sha, tree_id):
        from google.cloud import bigquery
        from google.cloud.bigquery import job as bq_job

        bq_client = self._connection

        metadata_table_name = self.__get_table_name(bq_client.table_prefix, self.METADATA_TABLE_NAME)
        staging_table_name = self.__get_table_name(bq_client.table_prefix, self.STAGING_TABLE_NAME)

        tree_id = tree_id.decode('utf8')
        random_token = b58encode(os.urandom(8))
        temp_table_name = 'tmp_{metadata_table_name}_{tree_id}_{random_token}'.format(
            metadata_table_name=metadata_table_name, tree_id=tree_id, random_token=random_token)

        def copy_to_temp():
            def create_temp_table():
                commit_temp_table = bq_dataset.table(temp_table_name)
                commit_temp_table.expires = datetime.datetime.utcnow() + datetime.timedelta(days=31)
                commit_temp_table.schema = self.__staging_table.schema
                commit_temp_table.create()

                return commit_temp_table

            def copy_to(commit_temp_table):
                copy_job = self.__copy_table(
                    commit_temp_table,
                    self.__staging_table,
                    bq_job.WriteDisposition.WRITE_TRUNCATE,
                    bq_job.CreateDisposition.CREATE_NEVER)
                copy_job.begin()

                self.handle_bq_errors(copy_job.result())

            new_temp_table = create_temp_table()
            copy_to(new_temp_table)

            return new_temp_table

        def query_to_temp(commit_temp_table):
            query = """
                #standardSQL
                SELECT _sha, @commit_sha as _commit_sha, *  EXCEPT(_sha, _commit_sha) FROM (
                  SELECT * EXCEPT(_max_sha, _max_ts) FROM {dataset_name}.{staging_table_name}
                  INNER JOIN (
                    SELECT _sha as _max_sha, MAX(_ts) as _max_ts
                    FROM {dataset_name}.{staging_table_name}
                    GROUP BY _sha
                  ) ON _sha = _max_sha
                  WHERE _max_ts = _ts
                )
            """.format(
                dataset_name=bq_dataset.name,
                staging_table_name=staging_table_name)

            query_parameters = (
                bigquery.ScalarQueryParameter('commit_sha', 'STRING', commit_sha),
            )

            query_job = self._query_async(query, query_parameters=query_parameters)
            query_job.destination = commit_temp_table
            query_job.write_disposition = bq_job.WriteDisposition.WRITE_EMPTY
            query_job.begin()

            self.handle_bq_errors(query_job.result())

        def begin_copy_to_metadata(commit_temp_table):
            copy_job = self.__copy_table(
                self.__metadata_table,
                commit_temp_table,
                bq_job.WriteDisposition.WRITE_APPEND,
                bq_job.CreateDisposition.CREATE_NEVER)
            copy_job.begin()
            self.handle_bq_errors(copy_job.result())

        def truncate_staging():
            self.__staging_table.delete()
            self.__staging_table = self.__create_specific_table(self.STAGING_TABLE_NAME, self.__staging_table.schema)

        with bq_client.get_cursor() as bq_dataset:
            temp_table = copy_to_temp()
            query_to_temp(temp_table)
            begin_copy_to_metadata(temp_table)
            truncate_staging()

    @classmethod
    def build_dict(cls, row, query_job):
        destination_table = query_job.destination
        return {
            cls.bq_field_name_to_common_name(field.name): val for field, val in zip(destination_table.schema, row)
        }

    def _query_head_data(self, sha_list):
        from google.cloud import bigquery

        bq_client = self._connection

        with bq_client.get_cursor() as bq_dataset:
            query = """
            #standardSQL
            SELECT * EXCEPT(_max_sha, _max_ts, _ts) FROM (SELECT *
              FROM {dataset_name}.{staging_table_name} WHERE _sha IN UNNEST(@sha_list)
              UNION ALL
                SELECT * FROM {dataset_name}.{metadata_table_name} WHERE _sha IN UNNEST(@sha_list)) as metadata_staging_combine
              INNER JOIN (
                SELECT  _sha as _max_sha, MAX(_ts) as _max_ts FROM {dataset_name}.{staging_table_name} WHERE _sha IN UNNEST(@sha_list) GROUP BY _sha
                UNION ALL
                  SELECT  _sha as _max_sha, MAX(_ts) as _max_ts FROM {dataset_name}.{metadata_table_name} WHERE _sha IN UNNEST(@sha_list) GROUP BY _sha
              ) _max_metadata
            ON
              metadata_staging_combine._sha = _max_sha
            WHERE
              metadata_staging_combine._ts = _max_ts;
            """.format(
                dataset_name=bq_dataset.name,
                staging_table_name=self.__get_table_name(bq_client.table_prefix, self.STAGING_TABLE_NAME),
                metadata_table_name=self.__get_table_name(bq_client.table_prefix, self.METADATA_TABLE_NAME))

            query_parameters = (
                bigquery.ArrayQueryParameter('sha_list', 'STRING', sha_list),
            )

            return self._query_sync(query, query_parameters, process_row=self.build_dict)

    def _query(self, sql_vars, select_fields, where):
        bq_client = self._connection

        with bq_client.get_cursor() as bq_dataset:
            query_sql = """
                 #Legacy SQL
                 select {select}
                  from {dataset_name}.{metadata_table_name}
                 where _ts IN (
                   SELECT MAX(_ts)
                   FROM {dataset_name}.{metadata_table_name}
                   GROUP BY _sha
                 ) AND {where}
                 ORDER BY _sha
             """.format(
                dataset_name=bq_dataset.name,
                metadata_table_name=self.__get_table_name(bq_client.table_prefix, self.METADATA_TABLE_NAME),
                where=where,
                select=','.join(select_fields))

            query_sql = self.fill_in_vars(query_sql, sql_vars)

            data = self._query_sync(query_sql, use_legacy_sql=True, process_row=self.build_dict)

            for result in data:
                yield unflatten(result, separator='.')
