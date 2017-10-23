from sqlalchemy import create_engine
from sqlalchemy.sql import text
from kck.lib.config import kck_config_lookup

db_connections = {}

class KCKDatabase(object):

    @classmethod
    def get_database(cls, dbname):
        global db_connections
        connection_url = kck_config_lookup("databases", dbname, "connection_url")
        if dbname not in db_connections:
            db_connections[dbname] = create_engine(connection_url).connect()
        return db_connections[dbname]

    @classmethod
    def query(cls, dbname, tmpl, params=None):
        dbconx = cls.get_database(dbname)
        stmt = text(tmpl, params)
        if params is not None:
            return dbconx.execute(stmt, params)
        return dbconx.execute(stmt)
