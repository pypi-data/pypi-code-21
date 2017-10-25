# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""`psycopg2` based database access."""
from sys import exc_info

from zope.component import adapter
from zope.publisher.interfaces import Retry
from zope.rdb import ZopeDatabaseAdapter, parseDSN

from psycopg2 import connect
from psycopg2._psycopg import cursor
from psycopg2.extensions import ISOLATION_LEVEL_SERIALIZABLE

from .zrdb import IDatabaseExecuteExceptionEvent

DNSMAP = dict(username="user")

class PgAdapter(ZopeDatabaseAdapter):
  def _connection_factory(self):
    conn_info = parseDSN(self.dsn)
    connection = connect(
      " ".join("%s=%s" % (DNSMAP.get(k, k), v) for (k, v) in conn_info.iteritems() if v)
      )
    connection.set_isolation_level(ISOLATION_LEVEL_SERIALIZABLE)
    return connection


@adapter(type(cursor), IDatabaseExecuteExceptionEvent)
def handle_exception(cursor, e):
  if isinstance(e.exc, TransactionRollbackError): raise Retry(exc_info())
           

