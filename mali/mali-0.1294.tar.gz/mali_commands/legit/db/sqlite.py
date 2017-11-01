# coding=utf-8
import random
import sys
from .base_connection import BaseConnection


class SqliteSqlHelper(object):
    def __init__(self):
        pass

    @classmethod
    def escape(cls, name):
        return '[%s]' % name

    @classmethod
    def random_function_name(cls):
        return 'ml_random'


class SqliteConnection(BaseConnection):
    def __init__(self, data_volume_config, **kwargs):
        self.__rnd = None
        super(SqliteConnection, self).__init__(data_volume_config, **kwargs)

    def _create_cursor(self):
        return self._native_conn.cursor()

    def _commit(self):
        self._native_conn.commit()

    def _rollback(self):
        self._native_conn.rollback()

    @classmethod
    def execute_multi(cls, cursor, multi_sql):
        for sql in multi_sql.split(';'):
            sql = sql.strip()
            if len(sql) == 0:
                continue

            cursor.execute(sql)

    def _create_connection(self, path=None, read_only=False, **kwargs):
        import sqlite3

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]

            return d

        def ml_random(seed):
            if self.__rnd is None:
                self.__rnd = random.Random(seed)

            return self.__rnd.random()

        if read_only and sys.version_info >= (3, 4):
            conn = sqlite3.connect('file:{path}?mode=ro'.format(path=path), uri=True)
        else:
            conn = sqlite3.connect(path)

        conn.row_factory = dict_factory
        conn.create_function("ml_random", 1, ml_random)

        return conn

    def create_sql_helper(self):
        return SqliteSqlHelper()
