# coding=utf-8
import logging
import six

from flatten_json import unflatten
from .base_metadata_db import BaseMetadataDB
from flatten_json import flatten

logger = logging.getLogger(__name__)


# noinspection SqlIdentifier,SqlResolve
class MySqlMetadataDB(BaseMetadataDB):
    create_table_sql = """
      BEGIN;
      CREATE TABLE IF NOT EXISTS `metadata` (
        `@sha` VARCHAR(128) NOT NULL,
        `@commit_sha` VARCHAR(128) NOT NULL,
        `@version` INT UNSIGNED NOT NULL,
        PRIMARY KEY (`@sha`, `@commit_sha`),
        INDEX `@idx_commit_sha` (`@commit_sha`),
        INDEX `@idx_version` (`@version`)
      );
      CREATE TABLE IF NOT EXISTS `versions` (
        `table` VARCHAR(128) NOT NULL,
        `version` INT UNSIGNED NOT NULL,
        PRIMARY KEY (`table`)
      );
      INSERT INTO `versions` (`table`, `version`) SELECT 'metadata', 0
        WHERE NOT EXISTS(SELECT 1 FROM `versions` WHERE `table` = 'metadata');
      COMMIT;
    """

    def __init__(self, connection):
        self.__prev_table_info = None
        super(MySqlMetadataDB, self).__init__(connection)

    def _create_table(self):
        with self._connection.get_cursor() as c:
            for result in c.execute(self.create_table_sql, multi=True):
                logger.info("'%s': %s", result.statement, result)

    @classmethod
    def __dict_gen_all(cls, cursor):
        field_names = [d[0].lower() for d in cursor.description]
        rows = cursor.fetchall()
        if not rows:
            return

        for row in rows:
            yield dict(zip(field_names, row))

    @classmethod
    def __dict_gen_one(cls, cursor):
        field_names = [d[0].lower() for d in cursor.description]
        row = cursor.fetchone()
        if not row:
            return

        return dict(zip(field_names, row))

    def __get_table_info(self):
        with self._connection.get_cursor() as c:
            c.execute("describe metadata")

            result = {}
            for column_info in self.__dict_gen_all(c):
                # noinspection PyTypeChecker
                result[column_info['field']] = column_info['type']

            return result

    def _add_missing_columns(self, data_object):
        flatten_data = flatten(data_object, separator='.')

        if self.__prev_table_info is None:
            table_info = self.__get_table_info()
            self.__prev_table_info = table_info

        self.__add_missing_columns_from_table_info(flatten_data)

    def __add_missing_columns_from_table_info(self, flatten_data):
        for column_name, column_value in flatten_data.items():
            if column_name not in self.__prev_table_info:
                self.__add_column(column_name, column_value)

    def __add_column(self, name, column_value):
        column_sql_type = self.__value_to_sql_type(column_value)

        with self._connection.get_cursor() as c:
            add_column = "ALTER TABLE metadata ADD COLUMN `{name}` {type}".format(name=name, type=column_sql_type)
            c.execute(add_column)

            add_index = "CREATE INDEX `idx_{name}` ON `metadata` (`{name}`)".format(name=name)
            c.execute(add_index)
            self._connection.commit()

            self.__prev_table_info = self.__get_table_info()

    @classmethod
    def __value_to_sql_type(cls, column_value):
        if isinstance(column_value, six.string_types):
            return 'VARCHAR(128)'

        if isinstance(column_value, six.integer_types):
            return 'INTEGER'

        if isinstance(column_value, (float, )):
            return 'DOUBLE'

        raise Exception('UNKNOWN TYPE %s' % type(column_value))

    def _query_head_data(self, sha_list):
        format_strings = ','.join(['%s'] * len(sha_list))

        get_row_sql = """
            select metadata.*
            from metadata
            inner join (
                SELECT `@sha` as `@__max_sha`, MAX(`@version`) as `_@max_version`
                FROM `metadata`
                WHERE `@sha` in (%s)
                GROUP BY `@sha`) _max
            on `@sha` = `@__max_sha`
            where `@version` = `_@max_version`;
        """ % format_strings

        with self._connection.get_cursor() as c:
            c.execute(get_row_sql, tuple(sha_list))
            return list(self.__dict_gen_all(c))

    def _add_data(self, flatten_data_list):
        fields = self.__prev_table_info.keys()

        values_params = ['%s'] * len(fields)

        values_list = []
        for flatten_data in flatten_data_list:
            values = []

            for field_name in fields:
                values.append(flatten_data.get(field_name))

            values_list.append(values)

        escape_fields = ['`%s`' % field_name for field_name in fields]

        insert_data_sql = "REPLACE INTO `metadata` ({fields}) values ({values_params})".format(
            fields=",".join(escape_fields), values_params=",".join(values_params))

        with self._connection.get_cursor() as c:
            c.executemany(insert_data_sql, values_list)

            self._connection.commit()

    def commit(self, commit_sha, tree_id):
        update_staging = """
          UPDATE `versions` SET `version` = `version` + 1 where `table` = 'metadata';
          UPDATE `metadata` SET `@commit_sha` = '{commit_sha}', `@version` = (SELECT `version` from `versions` where `table` = 'metadata') WHERE `@commit_sha` = 'staging';
        """

        update_staging = update_staging.format(commit_sha=commit_sha)

        with self._connection.get_cursor() as c:
            res = list(c.execute(update_staging, multi=True))

            self._connection.commit()

    def _query(self, sql_vars, select_fields, where):
        query_sql = """
             select {select}
             from `metadata`
             where `@version` IN (
               SELECT MAX(`@version`)
               FROM `metadata`
               GROUP BY `@sha`
             ) AND {where}
             ORDER BY `@sha`
         """.format(where=where, select=','.join(select_fields))

        query_sql = self.fill_in_vars(query_sql, sql_vars)

        for result in self._return_all_result_from_query(query_sql):
            yield result

    def get_data_for_commit(self, sha, commit_sha):
        raise NotImplementedError(self.get_data_for_commit)

    def get_all_data(self, sha):
        raise NotImplementedError(self.get_all_data)
