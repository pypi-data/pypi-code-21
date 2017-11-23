# coding: utf-8

import pandas as pd
from miceshare.db import mysql_access
import tushare as ts
from miceshare.util import vars
from miceshare.util.stock_utils import get_stock_code,get_stock_type


def import_all_securities():
    """
    导入股票列表数据
    :return:
    """
    all_securities = pd.read_csv("all_securities.csv")
    print(all_securities.head())
    for index, row in all_securities.iterrows():
        code = row[0]
        name = row[1]
        date = row[3]
        ex = get_stock_type(row[0])

        mysql_access.stock_dao.insert(code,name,date,ex)
    print("done")

def import_all_concept_classified():
    concept = ts.get_concept_classified()
    print(concept)
    for k,v in concept.iterrows():
        code = v['code']
        name = v['name']
        c_name = v['c_name']
        print(code,name,c_name)
        mysql_access.board_dao.insert(c_name,c_name,vars.Board_C)
        mysql_access.board_stock_dao.insert(code,c_name)

# import_all_securities
import_all_concept_classified()

# print(stock_dao.select('2017-11-22'))
# print(board_dao.select())
# print(board_stock_dao.select())