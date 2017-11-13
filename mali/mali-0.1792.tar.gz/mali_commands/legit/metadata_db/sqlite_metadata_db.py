# coding=utf-8
import six
from .base_metadata_db import BaseMetadataDB, unicode_dict_to_str
from flatten_json import unflatten
from flatten_json import flatten


class SqliteMetadataDB(BaseMetadataDB):
    create_table_sql = """
      CREATE TABLE IF NOT EXISTS metadata (
        '@sha' TEXT NOT NULL,
        '@commit_sha' TEXT NOT NULL,
        '@version' INTEGER,
        PRIMARY KEY ('@sha', '@commit_sha')
      );
      CREATE TABLE IF NOT EXISTS versions (
        'table' TEXT PRIMARY KEY,
        'version' INTEGER NOT NULL
      );
      CREATE INDEX IF NOT EXISTS [@idx_commit_sha] ON [metadata] ([@commit_sha]);
      CREATE INDEX IF NOT EXISTS [@idx_version] ON [metadata] ([@version]);
      INSERT INTO versions([table], [version]) SELECT 'metadata', 0
        WHERE NOT EXISTS(SELECT 1 FROM [versions] WHERE [table] = 'metadata');
    """

    def __init__(self, connection):
        self.__prev_table_info = None

        super(SqliteMetadataDB, self).__init__(connection)

    def __get_table_info(self):
        with self._connection.get_cursor() as c:
            table_info = c.execute("pragma table_info('metadata')").fetchall()

        result = {}
        for column_info in table_info:
            # noinspection PyTypeChecker
            result[column_info['name']] = column_info['type']

        return result

    def _create_table(self):
        with self._connection.get_cursor() as c:
            self._connection.execute_multi(c, self.create_table_sql)

            self._connection.commit()

    @classmethod
    def __value_to_sql_type(cls, column_value):
        if isinstance(column_value, six.string_types):
            return 'TEXT'

        if isinstance(column_value, six.integer_types):
            return 'INTEGER'

        if isinstance(column_value, (float,)):
            return 'REAL'

        raise Exception('UNKNOWN TYPE %s' % type(column_value))

    def __add_column(self, name, column_value):
        column_sql_type = self.__value_to_sql_type(column_value)

        with self._connection.get_cursor() as c:
            c.execute("ALTER TABLE metadata ADD COLUMN '{name}' {type}".format(name=name, type=column_sql_type))
            c.execute("CREATE INDEX 'idx_{name}' ON [metadata] ('{name}')".format(name=name))
            self._connection.commit()

        self.__prev_table_info = self.__get_table_info()

    def __add_missing_columns_from_table_info(self, flatten_data):
        for column_name, column_value in flatten_data.items():
            if column_name not in self.__prev_table_info:
                self.__add_column(column_name, column_value)

    def _add_missing_columns(self, data_object):
        flatten_data = flatten(data_object, separator='.')

        if self.__prev_table_info is None:
            table_info = self.__get_table_info()
            self.__prev_table_info = table_info

        self.__add_missing_columns_from_table_info(flatten_data)

    def _add_data(self, data_list):
        fields = self.__prev_table_info.keys()

        values_params = ['?'] * len(fields)

        values_list = []
        for data_object in data_list:
            flatten_data = flatten(data_object, separator='.')
            values = []

            for field_name in fields:
                values.append(flatten_data.get(field_name))

            values_list.append(values)

        escape_fields = ['[%s]' % field_name for field_name in fields]

        insert_data_sql = "INSERT OR REPLACE INTO [metadata] ({fields}) values ({values_params})".format(
            fields=",".join(escape_fields), values_params=",".join(values_params))

        with self._connection.get_cursor() as c:
            c.executemany(insert_data_sql, values_list)

            self._connection.commit()

    def get_data_for_commit(self, sha, commit_sha):
        get_row_sql = """
            SELECT *
            FROM [metadata]
            WHERE [@sha] = ? AND [@version] IN (
              SELECT MAX([@version])
              FROM [metadata]
              WHERE [@sha] = ? AND [@version] <= (SELECT [@version] FROM [metadata] WHERE [@commit_sha] = ? LIMIT 1)
              GROUP BY [@sha]
            )
        """

        with self._connection.get_cursor() as c:
            c.execute(get_row_sql, (sha, sha, commit_sha,))
            data = c.fetchone()

        if data is None:
            return None

        return unflatten(unicode_dict_to_str(data), separator='.')

    def _query_head_data(self, sha_list):
        format_strings = ','.join(['?'] * len(sha_list))

        get_row_sql = """
            select [metadata].*
            from [metadata]
            inner join (
                SELECT [@sha] as [@__max_sha], MAX([@version]) as [_@max_version]
                FROM [metadata]
                WHERE [@sha] in (%s)
                GROUP BY [@sha]) _max
            on [@sha] = [@__max_sha]
            where [@version] = [_@max_version];
        """ % format_strings

        with self._connection.get_cursor() as c:
            c.execute(get_row_sql, tuple(sha_list))
            for data in c.fetchall():
                yield unflatten(unicode_dict_to_str(data), separator='.')

    def get_all_data(self, sha):
        get_row_sql = """
            SELECT *
            FROM [metadata]
            WHERE [@sha] = ?
            ORDER BY [@version]
        """

        with self._connection.get_cursor() as c:
            c.execute(get_row_sql, (sha,))

            while True:
                results = c.fetchmany(1000)
                if not results:
                    break

                for result in results:
                    yield unflatten(unicode_dict_to_str(result), separator='.')

    def end_commit(self):
        self._connection.commit()

    def begin_commit(self, commit_sha, tree_id):
        update_version_sql = """
          UPDATE [versions] SET [version] = [version] + 1 WHERE [table] = 'metadata';
        """

        update_staging = """
          UPDATE [metadata] SET [@commit_sha] = '{commit_sha}', [@version] = (SELECT [version] FROM [versions] WHERE [table] = 'metadata') WHERE [@commit_sha] = 'staging';
        """

        update_staging = update_staging.format(commit_sha=commit_sha)

        with self._connection.get_cursor() as c:
            c.execute(update_version_sql)
            c.execute(update_staging)

    def _query(self, sql_vars, select_fields, where):
        query_sql = """
             select {select}
             from [metadata]
             where [@version] IN (
               SELECT MAX([@version])
               FROM [metadata]
               GROUP BY [@sha]
             ) AND {where}
             ORDER BY [@sha]
         """.format(where=where, select=','.join(select_fields))

        query_sql = self.fill_in_vars(query_sql, sql_vars)

        for result in self._return_all_result_from_query(query_sql):
            yield result
