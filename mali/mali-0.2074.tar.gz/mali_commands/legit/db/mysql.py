# coding=utf-8
from .base_connection import BaseConnection


class MySqlSqlHelper:
    @classmethod
    def escape(cls, name):
        return '`%s`' % name

    @classmethod
    def random_function_name(cls):
        return 'RAND'


class MySqlConnection(BaseConnection):
    def __init__(self, data_volume_config, **kwargs):
        super(MySqlConnection, self).__init__(data_volume_config, **kwargs)

    def _create_connection(self, database=None, user=None, password=None, host=None, **kwargs):
        import mysql.connector

        return mysql.connector.connect(user=user, password=password, host=host, database=database)

    def _create_cursor(self):
        return self._native_conn.cursor()

    def _commit(self):
        self._native_conn.commit()

    def _rollback(self):
        self._native_conn.rollback()

    def create_sql_helper(self):
        return MySqlSqlHelper()
