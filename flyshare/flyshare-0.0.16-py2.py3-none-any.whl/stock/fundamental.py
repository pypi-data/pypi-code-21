# -*- coding:utf-8 -*-
"""
Trading Data API
Created on 2017/10/27
@author: Rubing Duan
@group : abda
@contact: rubing.duan@gmail.com
"""

import pandas as pd
import lxml.html
from lxml import etree
import re
import time
from pandas.compat import StringIO
from flyshare.util import vars
import json
import bson.json_util as ju
import tushare as ts
import flyshare.util as util
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

def get_stock_basics(date=None, data_source = 'tushare'):
    """
        Get the basic info of Shanghai and Shenzhen listed companies
    Parameters
    date: YYYY-MM-DD，Default is the last trading day, currently only provide historical data after 2016-08-09

    Return
    --------
    DataFrame
               code,
               name,
               industry,
               area,
               pe,
               outstanding,
               totals,
               totalAssets,
               liquidAssets,
               fixedAssets,
               reserved,
               reservedPerShare,
               eps,
               bvps,
               pb,
               timeToMarket
    """
    if util.is_tushare(data_source):
        util.log_debug('Tushare Data:')
        return ts.get_stock_basics(date=date)
    elif util.is_flyshare(data_source):
        url = vars.DATA_SOURCE + '/stockbasics'
        if date is not None:
            url += '?date='+date
        data = json.loads(ju.loads(urlopen(url).read()))
        df = pd.DataFrame(data)
        if '_id' in df:
            df = df.drop('_id', 1)
        return df

def get_report_data(year, quarter, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_report_data(year, quarter)

def get_profit_data(year, quarter, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_profit_data(year, quarter)

def get_operation_data(year, quarter, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_operation_data(year, quarter)

def get_growth_data(year, quarter, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_growth_data(year, quarter)

def get_debtpaying_data(year, quarter, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_debtpaying_data(year, quarter)

def get_cashflow_data(year, quarter, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_cashflow_data(year, quarter)

def get_balance_sheet(code, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_balance_sheet(code)

def get_profit_statement(code, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_profit_statement(code)

def get_cash_flow(code, data_source = 'tushare'):
    if util.is_tushare(data_source):
        return ts.get_cash_flow(code)

if __name__ == '__main__':
    print get_stock_basics().head(2)