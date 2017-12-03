# -*- coding: utf8 -*-
from .base_connection import BaseConnection


class GAEDatastoreConnection(BaseConnection):
    def _create_connection(self, **kwargs):
        pass

    def _rollback(self):
        pass

    def _commit(self):
        pass

    def create_sql_helper(self):
        pass

    def _create_cursor(self):
        pass
