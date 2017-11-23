# coding=utf-8
#

import sqlite3
import datetime
from miceshare.util import vars

data_path = vars.sqlite3_data_path
create_sql = 'create table if not exists %s (code char(6) PRIMARY KEY, data text)'
select_sql = 'select * from %s'
select_which = 'select * from %s where code=?'
insert_sql = 'INSERT INTO %s VALUES (?,?)'


def get_db_name(data_type='default'):
    return data_type


def format_sql(sql, data):
    return sql % data


def get_table_name(data_type):
    now = datetime.date.today()
    if data_type == 'bs':
        return 'bs_' + now.strftime('%Y%m%d')


def login(db_name):
    conn = sqlite3.connect(data_path + db_name)
    return conn


def create_table(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    print('change', cursor.rowcount)
    conn.commit()


def create_if_not_exists(conn, data_type):
    table_name = get_table_name(data_type)
    create_sql_ = format_sql(create_sql, table_name)
    print(create_sql_)
    create_table(conn, create_sql_)


def insert_data(conn, data_type, data):
    table_name = get_table_name(data_type)
    sql = format_sql(insert_sql, (table_name))
    insert(conn, sql, data)


def insert(conn, sql, data):
    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        print('insert', cursor.rowcount)
        conn.commit()
    except:
        print('fail', data)


def query(conn, table_name, data=None):
    sql = None
    if data:
        sql = format_sql(select_which, (table_name))
    else:
        sql = format_sql(select_sql, (table_name))
    print(sql)
    cursor = conn.cursor()
    if data:
        print(sql, data)
        cursor.execute(sql, data)
    else:
        cursor.execute(sql)
    row = cursor.fetchone()
    return row


def query_all():
    conn = sqlite3.connect('d:/go/data/kpl')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bs_20171109')
    for r in cursor.fetchall():
        print(r)


def dump_data(conn, data_type, data):
    sql_ = None
    if data_type == 'bs':
        _sql = format_sql(insert_sql, get_table_name(data_type))

    insert(conn, _sql, data)


if __name__ == '__main__':
    conn = login('bs')
    # create_if_not_exists(conn, 'bs')
    query1 = query(conn, 'bs_20171113')
    print(query1)
