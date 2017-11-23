# coding: utf-8

import pandas as pd
from miceshare.db import mysql_access
import tushare as ts
from miceshare.util import vars


def get_stock_type(stock_code):
    """
    TODO 抽到工具类
    判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    stock_code = str(stock_code)
    if stock_code.startswith(('sh', 'sz')):
        return stock_code[:2]
    if stock_code.startswith(('50', '51', '60', '73', '90', '110', '113', '132', '204', '78')):
        return 'sh'
    if stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
        return 'sz'
    if stock_code.startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'


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