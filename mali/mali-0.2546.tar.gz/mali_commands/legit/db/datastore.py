# -*- coding: utf8 -*-
from .base_connection import BaseConnection


class DatastoreSqlHelper(object):
    def __init__(self):
        pass


class DatastoreConnection(BaseConnection):
    def __init__(self, data_volume_config, project, **kwargs):
        self.__project = project
        super(DatastoreConnection, self).__init__(data_volume_config, **kwargs)

    def _create_connection(self, **kwargs):
        from google.cloud import datastore

        return datastore.Client(project=self.__project, _use_grpc=False)

    @classmethod
    def create_entity(cls, key, exclude_from_indexes=None):
        from google.cloud import datastore
        return datastore.Entity(key, exclude_from_indexes=exclude_from_indexes or ())

    def _create_cursor(self):
        return self._native_conn

    def _commit(self):
        pass

    def _rollback(self):
        pass

    def create_sql_helper(self):
        return DatastoreSqlHelper()
