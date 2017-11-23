# coding=utf-8
#

import tushare as ts
import pandas as pd
import sqlite3
import miceshare.configs as configs

data_path = configs.data_path


def init_data():
    df = ts.get_stock_basics()
    conn = sqlite3.connect(data_path + 'default')
    df.to_sql(name='basic', con=conn, if_exists='replace')


def query_all_stocks():
    conn = sqlite3.connect(data_path + 'default')
    return pd.read_sql('select * from basic', con=conn)


if __name__ == '__main__':
    # init_data()
    stocks = query_all_stocks()
    print(stocks.head())
