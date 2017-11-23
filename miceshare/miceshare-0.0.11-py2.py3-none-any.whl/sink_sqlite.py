# coding=utf-8
#

import requests
import sqlite3
import datetime
import pandas as pd
import logging


logging.basicConfig(level=logging.INFO,
                    filename='/tmp/stock.log',
                    filemode='w',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

def get_bs(code):
    data = {'c': 'StockL2Data', 'a': 'GetStockBsvolume', 'apiv': 'w5'}
    data['StockID'] = code
    url = "http://hq.kaipanla.com/w1/api/index.php"
    headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.0; BLN-AL10 Build/HONORBLN-AL10)",
               "Host": "hq.kaipanla.com"
               }
    post = requests.post(url, data=data, headers=headers)
    try:
        if post.status_code == 200:
            return post.text
    except:
        logging.info('get bs fail %s', code)
    return None


def create_table(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    logging.info('init table %s', cursor.rowcount)
    conn.commit()


def insert(conn, sql, data):
    try:
        if data:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            logging.info('insert %s', cursor.rowcount)
            conn.commit()
    except:
        logging.info('fail %s', data)


if __name__ == '__main__':
    now = datetime.datetime.now()
    logging.info('start dump %s', now)
    conn = sqlite3.connect('/stock/data/bs_' + now.strftime('%Y%m'))
    table_name = 'bs_' + now.strftime('%Y%m%d')
    create_sql = 'create table if not exists %s (code char(6) PRIMARY KEY, data text)'
    insert_sql = 'INSERT INTO %s VALUES (?,?)'
    create_sql_ = create_sql % (table_name)
    create_table(conn, create_sql_)
    logging.info('create table: %s', table_name)
    conn_def = sqlite3.connect('/stock/data/default')
    stocks = pd.read_sql('select * from basic', con=conn_def)
    insert_sql_ = insert_sql % (table_name)
    for code in stocks['code']:
        logging.info('dump %s', code)
        bs = get_bs(code)
        insert(conn, insert_sql_, (code, bs))
