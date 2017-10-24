from __future__ import unicode_literals
import functools

from .dbapi import DbAPIConnectionInterceptor, DbAPICursorInterceptor
from ..base import ExitCallInterceptor


class TormysqlInterceptor(ExitCallInterceptor):
    def end_exit_call(self, exit_call, future=None, exc_info=None):
        if exc_info or not future:
            super(TormysqlInterceptor, self).end_exit_call(exit_call, exc_info=exc_info)
            return

        import tornado.stack_context

        def end_exit_call(exit_call, completed_future):
            super(TormysqlInterceptor, self).end_exit_call(exit_call, exc_info=completed_future.exc_info())

        if future.done():
            end_exit_call(exit_call, future)
        else:
            future._callbacks.insert(0, tornado.stack_context.wrap(functools.partial(end_exit_call, exit_call)))


class TormysqlConnectionInterceptor(TormysqlInterceptor, DbAPIConnectionInterceptor):
    def get_backend_properties(self, client, *args, **kwargs):
        host = client._kwargs.get('host', 'localhost')
        port = client._kwargs.get('port', '3306')
        db = client._kwargs.get('database', client._kwargs.get('db', ''))
        return host, port, db, 'TORMYSQL'


class TormysqlCursorInterceptor(TormysqlInterceptor, DbAPICursorInterceptor):
    def get_connection(self, cursor):
        # Since in the `connect` interceptor we are actually setting attributes
        # on the client, not the connection, we need to return it here.
        # Getting the client instance from the bound callback is horrible, but
        # it's the only way I could manage to get at it.
        return cursor.connection._close_callback.__self__


def intercept_tormysql_client(agent, mod):
    TormysqlConnectionInterceptor(agent, mod.Client, TormysqlCursorInterceptor).attach('connect')
