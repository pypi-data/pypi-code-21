# coding=utf-8
from .base_connection import BaseConnection


class SpannerSqlHelper(object):
    def __init__(self):
        pass

    @classmethod
    def escape(cls, name):
        return '`%s`' % name

    @classmethod
    def random_function_name(cls):
        return 'RAND'


class SpannerConnection(BaseConnection):
    def __init__(self, data_volume_config, project, instance, database, **kwargs):
        self.__database = database
        self.__instance = instance
        self.__project = project
        super(SpannerConnection, self).__init__(data_volume_config, **kwargs)

    def _create_connection(self, **kwargs):
        from google.cloud import spanner

        spanner_client = spanner.Client(project=self.__project, credentials=credentials)
        return spanner_client.instance(self.__instance)

    def _create_cursor(self):
        return self._native_conn.database(self.__database)

    def _commit(self):
        pass

    def _rollback(self):
        pass

    def create_sql_helper(self):
        return SpannerSqlHelper()
