

import psycopg2

from elasticsearch import Elasticsearch

from datalab.src.loggers import datalab_loggers

#Alog Connection
DB_SESSION = "dbname=alog host=nico.pl.eso.org user=alogreader"


datalab_logger_object = datalab_loggers.datalab_logger(my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
datalab_logger_connections= datalab_logger_object.datalab_logger

def db_connection_setUp(db_session):
    """
    Creates a new database session

    :param db_session: String database propierties example alogdb: db_session='dbname=alog host=nico.pl.eso.org user=alogreader'
    :type db_session: String
    :return: connection instance

    note:: see http://initd.org/psycopg/docs/module.html
    """
    db_connection = psycopg2.connect(db_session)
    db_connection.set_client_encoding("latin1")
    return db_connection


def db_execute_query(db_connection, query, query_args):
    """
    Execute a query in a database sesion

    :param db_connection: connection db instance
    :param query: String query. example "SELECT * FROM alog WHERE timestamp BETWEEN %s and %s"
    :param query_args: tuple of args of the query. example (time.time(), time.time()-10)
    :type db_connection: Connection
    :type query: String
    :type query_args: tuple
    :return: cursor

    note:: see http://initd.org/psycopg/docs/usage.html
    """
    cursor = db_connection.cursor()
    #datalab_logger_connections.info("reading database[Query. May Take Time]...")
    cursor.execute(query, query_args)
    #datalab_logger_connections.info("finish to query database")
    return cursor


def es_connection_setUp(es_server):
    """
    Establish a elasticsearch connection
    :param es_server:
    :return: connection objetc
    """
    datalab_logger_connections.info("ES : setUp connection")
    return  Elasticsearch(es_server, timeout=30, ignore=[400, 404],  maxsize=100)