# coding=utf-8

import numpy as np
import pandas as pd

from .constants import *
from .utils import request_dataframe


def get_day_today_quote(dropna=False):
    """
    得到今日个股实时股价数据（包括停牌的股）
    :param dropna: 是否删除空行（即是否包括停牌的股）
    :return: DataFrame
    """
    df = request_dataframe(TODAY_QUOTE_FILE, dtype={0: np.str})

    if dropna:
        df.dropna(inplace=True)

    df.set_index(df.columns[0], inplace=True)
    df.index.name = None
    df['time'] = pd.to_datetime(df['time'])

    return df


def get_day_today_money(dropna=False):
    """
    得到今日个股实时资金数据（包括停牌的股）
    :param dropna: 是否删除空行（即是否包括停牌的股）
    :return: DataFrame
    """
    df = request_dataframe(TODAY_MONEY_FILE, dtype={0: np.str})

    if dropna:
        df.dropna(inplace=True)

    df.set_index(df.columns[0], inplace=True)
    df.index.name = None
    df['time'] = pd.to_datetime(df['time'])

    return df
