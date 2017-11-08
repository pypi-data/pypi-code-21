# coding=utf-8
import datetime
import logging

import six
from ..bigquery_mixin import BigQueryMixin
from .base_metadata_db import BaseMetadataDB, MetadataTypeNotSupported
from flatten_json import unflatten


# noinspection SqlNoDataSourceInspection
class BigQueryMetadataDB(BaseMetadataDB, BigQueryMixin):
    STAGING_TABLE_NAME = 'staging'
    METADATA_TABLE_NAME = 'metadata'
    INDEX_TABLE_NAME = 'index'
    STAGING_INDEX_TABLE_NAME = 'staging_index'

    def __init__(self, connection, version=None, delete_temp_on_commit=True):
        self.__version = version
        self.__staging_table = None
        self.__metadata_table = None
        self.__prev_table_info = None
        self.__delete_temp_on_commit = delete_temp_on_commit
        super(BigQueryMetadataDB, self).__init__(connection)

    def __get_staging_table_name(self):
        version = self.__version or 0
        return '%s_%s' % (self.STAGING_TABLE_NAME, version)

    def __get_staging_index_table_name(self):
        version = self.__version or 0
        return '%s_%s' % (self.STAGING_INDEX_TABLE_NAME, version)

    @classmethod
    def _default_table_schema(cls):
        from google.cloud import bigquery

        schema = (
            bigquery.SchemaField('_sha', 'STRING'),
            bigquery.SchemaField('_commit_sha', 'STRING'),
            bigquery.SchemaField('_ts', 'TIMESTAMP'),
            bigquery.SchemaField('_hash', 'STRING'),
            bigquery.SchemaField('url', 'STRING'),
        )

        return schema

    def _create_table(self):
        schema = self._default_table_schema()

        self.__metadata_table = self._create_specific_table(self.METADATA_TABLE_NAME, schema)
        self.__staging_table = self._create_specific_table(self.__get_staging_table_name(), self.__metadata_table.schema)

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

    def _patch_table_with_new_schema(self, table, schema):
        bq_client = self._connection

        table.schema = schema
        bq_client.update_table(table, ['schema'])

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
                    row.append(flatten_data_list.get(common_field_name))

            rows.append(row)

        bq_client = self._connection
        bq_client.create_rows(self.__staging_table, rows)

    def __truncate_staging(self):
        if not self.__delete_temp_on_commit:
            logging.debug('meta: delete_temp_on_commit')
            return

        logging.info('truncate metadata staging')
        bq_client = self._connection
        bq_client.delete_table(self._get_table_ref(self.__get_staging_table_name()))

    def end_commit(self):
        logging.debug('bq end commit meta')

        self.__truncate_staging()

    def begin_commit(self, commit_sha, tree_id):
        logging.debug('bq begin commit meta %s %s', commit_sha, tree_id)

        from google.cloud import bigquery

        staging_table = self._get_table_ref(self.__get_staging_table_name())
        index_staging_table = self._get_table_ref(self.__get_staging_index_table_name())
        metadata_table = self._get_table_ref(self.METADATA_TABLE_NAME)

        with self._connection.get_cursor() as bq_dataset:
            src_query = """
                #standardSQL
                SELECT @commit_sha as _commit_sha, * 
                # Find the latest metadata given in the staging meta
                FROM (
                  SELECT * EXCEPT(row_number)
                  FROM (
                    # Find the latest metadata given in the staging meta
                    SELECT * EXCEPT(_hash, _commit_sha) , ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number 
                    FROM {dataset_name}.{staging_table_name} 
                  )
                  WHERE row_number = 1
                )  
            """.format(
                dataset_name=bq_dataset.dataset_id,
                staging_table_name=staging_table.table_id,
                staging_index_table_name=index_staging_table.table_id)

            src_query_parameters = (
                bigquery.ScalarQueryParameter('commit_sha', 'STRING', commit_sha),
            )

            self._copy_table_data(src_query, src_query_parameters, metadata_table)

    def _query_head_data(self, sha_list):
        from google.cloud import bigquery
        from google.cloud.bigquery import QueryJobConfig

        bq_client = self._connection

        with bq_client.get_cursor() as bq_dataset:
            query = """
            #standardSQL
            SELECT * EXCEPT(_max_sha, _max_ts, _ts) FROM (SELECT *
              FROM `{dataset_name}.{staging_table_name}` WHERE _sha IN UNNEST(@sha_list)
              UNION ALL
                SELECT * FROM `{dataset_name}.{metadata_table_name}` WHERE _sha IN UNNEST(@sha_list)) as metadata_staging_combine
              INNER JOIN (
                SELECT  _sha as _max_sha, MAX(_ts) as _max_ts FROM `{dataset_name}.{staging_table_name}` WHERE _sha IN UNNEST(@sha_list) GROUP BY _sha
                UNION ALL
                  SELECT  _sha as _max_sha, MAX(_ts) as _max_ts FROM `{dataset_name}.{metadata_table_name}` WHERE _sha IN UNNEST(@sha_list) GROUP BY _sha
              ) _max_metadata
            ON
              metadata_staging_combine._sha = _max_sha
            WHERE
              metadata_staging_combine._ts = _max_ts;
            """.format(
                dataset_name=bq_dataset.dataset_id,
                staging_table_name=self._get_table_name(bq_client.table_prefix, self.__get_staging_table_name()),
                metadata_table_name=self._get_table_name(bq_client.table_prefix, self.METADATA_TABLE_NAME))

            query_parameters = (
                bigquery.ArrayQueryParameter('sha_list', 'STRING', sha_list),
            )

            job_config = QueryJobConfig()
            job_config.query_parameters = query_parameters

            items_iter, _ = self._query_sync(query, job_config, process_row=self.build_dict)

            return items_iter

    def _query(self, sql_vars, select_fields, where, max_results=None, start_index=None):
        import google.cloud.exceptions
        from google.cloud.bigquery import QueryJobConfig

        bq_client = self._connection

        metadata_table_name = self._get_table_name(bq_client.table_prefix, self.METADATA_TABLE_NAME)
        staging_table_name = self._get_table_name(bq_client.table_prefix, self.__get_staging_table_name())
        staging_index_table_name = self._get_table_name(bq_client.table_prefix, self.__get_staging_index_table_name())
        index_table_name = self._get_table_name(bq_client.table_prefix, self.INDEX_TABLE_NAME)

        limit = sql_vars.get('limit')
        limit = 'LIMIT %s' % limit if limit is not None else ''

        def query_staging():
            query = """
                #standardSQL
                SELECT url as _url, * EXCEPT(_ts, url)
                FROM ( # Bring all the items from staging index (except the metadata files)
                  SELECT *
                  FROM (
                    SELECT name as _sha
                    FROM (
                      SELECT *, ROW_NUMBER() OVER (PARTITION BY name) row_number
                      FROM {dataset_name}.{staging_index_table_name}
                      WHERE ENDS_WITH(name, '.metadata') = FALSE 
                     )
                    WHERE row_number = 1
                  ) staging_index
                  FULL JOIN (
                    SELECT _sha
                    FROM (
                      SELECT _sha, ROW_NUMBER() OVER (PARTITION BY _sha) row_number
                      FROM {dataset_name}.{staging_table_name}
                    )
                    WHERE row_number = 1    
                  ) staging_meta
                  USING(_sha)  
                ) AS staging_items
                LEFT JOIN ( 
                  # join this with latest (max _ts) metadata
                  SELECT * EXCEPT(_commit_sha)
                  FROM (
                    SELECT * EXCEPT(_hash, url)
                    FROM {dataset_name}.{staging_table_name}
                    UNION ALL
                    SELECT * EXCEPT(_hash, url)
                    FROM {dataset_name}.{metadata_table_name}
                    WHERE _ts = (
                        SELECT MAX(_ts)
                        FROM (
                          SELECT *
                          FROM {dataset_name}.{staging_table_name}
                          UNION ALL
                          SELECT *
                          FROM {dataset_name}.{metadata_table_name}
                        ) 
                        GROUP BY _sha
                        LIMIT 1
                      )
                  ) meta
                  RIGHT JOIN ( 
                    # This join will give us the latest URL (url) and hash (_hash) of the data (by name)
                    SELECT name as _sha, sha as _hash, url
                    FROM ( # This will remove any duplicates we might have
                      SELECT * EXCEPT(row_number)
                      FROM (
                        SELECT *, ROW_NUMBER() OVER (PARTITION BY name) row_number
                        FROM (
                          SELECT *
                          FROM {dataset_name}.{staging_index_table_name}
                          UNION ALL
                          SELECT *
                          FROM {dataset_name}.{index_table_name}
                          ORDER by ts DESC
                        ) 
                      )
                      WHERE row_number = 1
                    )
                  ) index_with_hash
                  USING(_sha)
                ) AS meta
                USING(_sha)
                WHERE({where})
                ORDER BY _ts DESC, _sha
                {limit}
             """.format(
                dataset_name=bq_dataset.dataset_id,
                index_table_name=index_table_name,
                staging_table_name=staging_table_name,
                metadata_table_name=metadata_table_name,
                staging_index_table_name=staging_index_table_name,
                where=where or 'True',
                select=','.join(select_fields),
                limit=limit)

            return query

        def query_all_meta_data_without_staging(version):
            query = """
                #standardSQL
                SELECT * EXCEPT(_ts, row_number)
                FROM (                
                    SELECT * EXCEPT(_phr), ROW_NUMBER() OVER (PARTITION BY _hash ORDER BY _ts DESC) row_number
                    FROM (
                        SELECT CASE 
                          WHEN _phr >= $phase_train_start AND _phr < $phase_train_end THEN 'train'
                          WHEN _phr >= $phase_test_start AND _phr < $phase_test_end THEN 'test'
                          WHEN _phr >= $phase_validation_start AND _phr < $phase_validation_end THEN 'validation'
                          ELSE NULL
                        END as _phase, * EXCEPT(_hash, url)
                        FROM (
                          SELECT ((FARM_FINGERPRINT(CONCAT(_sha, '$seed')) + POW(2, 63)) / POW(2, 64)) as _phr, * FROM {dataset_name}.{metadata_table_name} 
                          WHERE _ts <= ( 
                            SELECT MAX(_ts) 
                            FROM {dataset_name}.{metadata_table_name} 
                            WHERE _commit_sha = '{version}' 
                            LIMIT 1
                          ) 
                        )
                        WHERE ({where})
                    ) 
                    LEFT JOIN (
                        # This join will give us the latest URL (url) and hash (_hash) of the data (by name)
                        SELECT name as _sha, sha as _hash, url as _url
                        FROM ( 
                        # This will remove any duplicates we might have
                          SELECT * EXCEPT(row_number)
                          FROM (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY name) row_number
                            FROM {dataset_name}.{index_table_name}
                            WHERE ts <= ( 
                              SELECT MAX(_ts) 
                              FROM {dataset_name}.{metadata_table_name}
                              WHERE _commit_sha = '{version}'
                              LIMIT 1
                            ) 
                            ORDER by ts DESC
                          )
                          WHERE row_number = 1
                        )
                    )
                    USING(_sha)
                    ORDER BY FARM_FINGERPRINT(CONCAT(_sha, '$seed'))
                )
                WHERE row_number = 1
                {limit}              
             """.format(
                dataset_name=bq_dataset.dataset_id,
                version=version,
                metadata_table_name=metadata_table_name,
                index_table_name=index_table_name,
                where=where or 'True',
                select=','.join(select_fields),
                limit=limit)

            return query

        def query_everything():
            query = """
                 #Legacy SQL
                 select {select} EXCEPT(_ts)
                  from (
                    select * from `{dataset_name}.{metadata_table_name}`
                    UNION ALL
                    SELECT
                      * EXCEPT(row_number)
                    FROM (
                      SELECT
                        *,
                        ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                      FROM
                        {dataset_name}.{staging_table_name})
                    WHERE
                      row_number = 1                              
                  ) 
                 where _ts IN (
                   SELECT MAX(_ts)
                   FROM {dataset_name}.{metadata_table_name}
                   GROUP BY _sha
                 ) AND ({where})
                 ORDER BY RAND($seed)
                 {limit}
             """.format(
                dataset_name=bq_dataset.dataset_id,
                metadata_table_name=metadata_table_name,
                staging_table_name=staging_table_name,
                where=where or 'True',
                select=','.join(select_fields),
                limit=limit)

            return query

        def _data_iter():
            for result in data_iter:
                for key, val in result.items():
                    if isinstance(val, six.string_types):
                        result[key] = val.encode('utf8')

                # if we don't have commit sha it means that this is a staging query
                result.setdefault('@commit_sha', 'staging')

                yield unflatten(result, separator='.')

        with bq_client.get_cursor() as bq_dataset:
            version_var = sql_vars.get('version')

            if version_var is None:
                query_sql = query_everything()
            elif version_var.lower() == 'staging':
                query_sql = query_staging()
            else:
                query_sql = query_all_meta_data_without_staging(version_var.lower())

            query_sql = self.fill_in_vars(query_sql, sql_vars)

            try:
                job_config = QueryJobConfig()

                data_iter, total_rows = self._query_sync(query_sql, job_config, max_results=max_results, start_index=start_index, process_row=self.build_dict)

                return _data_iter(), total_rows
            except google.cloud.exceptions.NotFound:
                return [], 0

    def get_all_data(self, sha):
        pass

    def get_data_for_commit(self, sha, commit_sha):
        pass
