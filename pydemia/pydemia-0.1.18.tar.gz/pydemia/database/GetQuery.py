import pandas as pd
from pandas import DataFrame as df
from datetime import datetime

import psycopg2 as pg
import sqlalchemy as sa
# import ibm_db
# import ibm_db_sa
import cx_Oracle as co
import pymysql


def postgreSQL(query, h=None, port=None, db=None, u=None, p=None):

    print('Using PostgreSQL')

    # DB Connection
    conn = pg.connect(host=h, port=str(port), user=u, password=p)
    start_tm = datetime.now()
    print(' Start :', str(start_tm))

    # Get a DataFrame
    query_result = pd.read_sql(query, conn)

    # Cloase Connection
    end_tm = datetime.now()
    print(' Finish :', str(end_tm))
    print('Elapsed :', str(end_tm - start_tm))
    conn.close()

    return query_result


def db2SQL(query, h=None, port=None, db=None, u=None, p=None):

    print('Using IBM DB2')

    # DB Connection
    connStr = 'ibm_db_sa://{}:{}@{}:{}/{}'
    engine = sa.create_engine(connStr.format(u, p, h, str(port), db))
    conn = engine.connect()
    start_tm = datetime.now()
    print(' Start :', str(start_tm))

    # Get a DataFrame
    execonn = engine.execute(query)

    query_result = df(execonn.fetchall())
    query_result.columns = execonn.keys()

    # Close Connection
    end_tm = datetime.now()
    print(' Finish :', str(end_tm))
    print('Elapsed :', str(end_tm - start_tm))
    conn.close()

    return query_result


def oracleSQL(query, h=None, port=None, db=None, u=None, p=None):

    print('Using OracleDB')

    # DB Connection
    dnsStr = co.makedsn(h, str(port), db)
    dnsStr = dnsStr.replace('SID', 'SERVICE_NAME')
    conn = co.connect(u, p, dnsStr)
    start_tm = datetime.now()

    # Get a DataFrame
    query_result = pd.read_sql(query, conn)

    # Close Connection
    end_tm = datetime.now()
    print(' Finish :', str(end_tm))
    print('Elapsed :', str(end_tm - start_tm))
    conn.close()

    return query_result


def mariaDB(query, h=None, port=None, db=None, u=None, p=None):

    print('Using MariaDB')

    # DB Connection
    conn = pymysql.connect(host=h, port=p, user=u, password=p, database=db)
    start_tm = datetime.now()
    print(' Start :', str(start_tm))

    # Get a DataFrame
    query_result = pd.read_sql(query, conn)

    # Close Connection
    end_tm = datetime.now()
    print(' Finish :', str(end_tm))
    print('Elapsed :', str(end_tm - start_tm))
    conn.close()

    return query_result
