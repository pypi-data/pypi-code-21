# -*- coding:utf-8 -*- 
"""
交易数据接口 
Created on 2017/10/27
@author: Rubing Duan
@group : abda
@contact: rubing.duan@gmail.com
"""
from __future__ import division

import time
import json
import urllib2
from bson.json_util import loads
import pandas as pd
import numpy as np
from pymongo import MongoClient
from flyshare.stock import cons as ct
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

import json
import bson.json_util as ju

def get_mongo_client(ip='127.0.0.1', port=27017):
    client = MongoClient(ip, port=port)
    return client


def get_stock_data(code=None, start=None, end=None):
    """
        获取个股历史交易记录
    Parameters
    ------
      code:string
                  股票代码 e.g. 600848
      start:string
                  开始日期 format：YYYY-MM-DD 为空时取到API所提供的最早日期数据
      end:string
                  结束日期 format：YYYY-MM-DD 为空时取到最近一个交易日数据
      ktype：string
                  数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
      retry_count : int, 默认 3
                 如遇网络等问题重复执行的次数
      pause : int, 默认 0
                重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
    return
    -------
      DataFrame
          属性:日期 ，开盘价， 最高价， 收盘价， 最低价， 成交量， 价格变动 ，涨跌幅，5日均价，10日均价，20日均价，5日均量，10日均量，20日均量，换手率
    """
    url = ct.DATA_SOURCE+'/stock?'
    if code is None:
        return None
    else:
        url += 'code='+code

    if start is not None:
        url += '&start='+start
    if end is not None:
        url += '&end='+end

    data = json.loads(ju.loads(urlopen(url).read()))
    df = pd.DataFrame(data)
    df = df.drop('_id',1)
    return df



def get_hist_data(code=None, start=None, end=None,
                  ktype='D', retry_count=3,
                  pause=0.001):
    """
        获取个股历史交易记录
    Parameters
    ------
      code:string
                  股票代码 e.g. 600848
      start:string
                  开始日期 format：YYYY-MM-DD 为空时取到API所提供的最早日期数据
      end:string
                  结束日期 format：YYYY-MM-DD 为空时取到最近一个交易日数据
      ktype：string
                  数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
      retry_count : int, 默认 3
                 如遇网络等问题重复执行的次数 
      pause : int, 默认 0
                重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
    return
    -------
      DataFrame
          属性:日期 ，开盘价， 最高价， 收盘价， 最低价， 成交量， 价格变动 ，涨跌幅，5日均价，10日均价，20日均价，5日均量，10日均量，20日均量，换手率
    """
    symbol = _code_to_symbol(code)
    url = ''
    if ktype.upper() in ct.K_LABELS:
        url = ct.DAY_PRICE_URL%(ct.P_TYPE['http'], ct.DOMAINS['ifeng'],
                                ct.K_TYPE[ktype.upper()], symbol)
    elif ktype in ct.K_MIN_LABELS:
        url = ct.DAY_PRICE_MIN_URL%(ct.P_TYPE['http'], ct.DOMAINS['ifeng'],
                                    symbol, ktype)
    else:
        raise TypeError('ktype input error.')
    
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            request = Request(url)
            lines = urlopen(request, timeout = 10).read()
            if len(lines) < 15: #no data
                return None
        except Exception as e:
            print(e)
        else:
            js = json.loads(lines.decode('utf-8') if ct.PY3 else lines)
            cols = []
            if (code in ct.INDEX_LABELS) & (ktype.upper() in ct.K_LABELS):
                cols = ct.INX_DAY_PRICE_COLUMNS
            else:
                cols = ct.DAY_PRICE_COLUMNS
            if len(js['record'][0]) == 14:
                cols = ct.INX_DAY_PRICE_COLUMNS
            df = pd.DataFrame(js['record'], columns=cols)
            if ktype.upper() in ['D', 'W', 'M']:
                df = df.applymap(lambda x: x.replace(u',', u''))
                df[df==''] = 0
            for col in cols[1:]:
                df[col] = df[col].astype(float)
            if start is not None:
                df = df[df.date >= start]
            if end is not None:
                df = df[df.date <= end]
            if (code in ct.INDEX_LABELS) & (ktype in ct.K_MIN_LABELS):
                df = df.drop('turnover', axis=1)
            df = df.set_index('date')
            df = df.sort_index(ascending = False)
            return df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)


def _code_to_symbol(code):
    """
        生成symbol代码标志
    """
    if code in ct.INDEX_LABELS:
        return ct.INDEX_LIST[code]
    else:
        if len(code) != 6 :
            return code
        else:
            return 'sh%s'%code if code[:1] in ['5', '6', '9'] else 'sz%s'%code