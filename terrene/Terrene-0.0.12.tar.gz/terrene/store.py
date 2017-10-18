import pandas
from .apps import BaseAppManager, BaseApp


class AbstractWarehouse(BaseApp):
    def create_table(self, table):
        return self.act(['tables', 'create'], {
            'object_id': self.object_id, 'table': table})

    def drop_table(self, table):
        return self.act(['tables', 'partial_update'], {
            'object_id': self.object_id, 'table': table})

    def read_row(self, table, key):
        return pandas.Series(self.act(['read_row'], {
            'object_id': self.object_id, 'table': table, 'key': key}))

    def read_rows(self, *args, **kwargs):
        table = kwargs['table']
        query = kwargs.get('query')
        select = kwargs.get('select')

        body = {'object_id': self.object_id, 'table': table}
        if query is not None:
            body['query'] = query
        if select is not None:
            body['select'] = select
        return pandas.DataFrame(self.act(['read_rows'], body))

    def write_row(self, table, row):
        return self.act(['write_row'], {
            'object_id': self.object_id, 'table': table, 'row': row})


class AbstractWarehouseManager(BaseAppManager):
    namespace = ['store', 'all']
    model = AbstractWarehouse


class StandardWarehouseManager(AbstractWarehouseManager):
    namespace = ['store', 'azure']


class SQLDatabase(AbstractWarehouse):
    def read_rows(self, query=None):
        return pandas.DataFrame(self.act(['read_rows'], {
            'object_id': self.object_id, 'query': query}))

    def read_row(self, table, key):
        raise NotImplementedError(
            'SQLDatabase does not support reading a single row. Please use read_rows instead.')

    def test_connection(self):
        return self.act(['test_connection'], {'object_id': self.object_id})


class SQLDatabaseManager(AbstractWarehouseManager):
    model = SQLDatabase
    namespace = ['store', 'sql']
