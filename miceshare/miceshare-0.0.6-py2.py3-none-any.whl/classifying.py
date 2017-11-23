# -*- coding:utf-8 -*-

"""
获取股票分类数据接口 

"""

import pandas as pd
from miceshare.db.mysql_access import stock_dao,board_dao,board_stock_dao
import datetime
from functools import lru_cache


def get_industry_classified():
    """
        获取行业分类数据
    Returns
    -------
    DataFrame
        code :股票代码
        name :股票名称
        c_name :行业名称
    """
    pass

@lru_cache(None)
def get_concept_for_stock(stock):
    """
        获取概念列表
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        c_name :概念名称
    """
    concept = get_concept_classified()
    return concept[concept['stock_code'] == stock]['board'].tolist()


@lru_cache(None)
def get_concept_classified():
    """
        获取概念分类数据
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        c_name :概念名称
    """
    l = board_stock_dao.select()
    return pd.DataFrame(l, columns=['stock_code', 'board'])


def get_area_classified():
    """
        获取地域分类数据
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        area :地域名称
    """
    pass


def get_gem_classified():
    """
        获取创业板股票
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    df = get_stock_basics()
    df = df.ix[df.code.str[0] == '3']
    df = df.sort_values('code').reset_index(drop=True)
    return df
    

def get_sme_classified():
    """
        获取中小板股票
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    df = get_stock_basics()
    df = df.ix[df.code.str[0:3] == '002']
    df = df.sort_values('code').reset_index(drop=True)
    return df 

def get_st_classified():
    """
        获取风险警示板股票
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    df = get_stock_basics
    df.reset_index(inplace=True)
    df = df.ix[df.name.str.contains('ST')]
    df = df.sort_values('code').reset_index(drop=True)
    return df 

@lru_cache(None)
def get_stock_basics(time=None):
    """
    查询股票列表
    :param time 截止上市日期
    :return:
    DataFrame
        code :股票代码
        name :股票名称
        start_date :日期
        exchange:市场 sz或sh
    """
    if time is None:
        time = datetime.datetime.now().date()
    l = stock_dao.select(time)
    return pd.DataFrame(l,columns=['code','name','start_date','exchange'])

def get_hs300s():
    """
    获取沪深300当前成份股及所占权重
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        date :日期
        weight:权重
    """
    pass


def get_sz50s():
    """
    获取上证50成份股
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    pass


def get_zz500s():
    """
    获取中证500成份股
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    pass


def get_terminated():
    """
    获取终止上市股票列表
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        oDate:上市日期
        tDate:终止上市日期 
    """
    pass


def get_suspended():
    """
    获取暂停上市股票列表
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        oDate:上市日期
        tDate:终止上市日期 
    """
    pass

