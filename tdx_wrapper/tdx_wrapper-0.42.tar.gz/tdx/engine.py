from pytdx.hq import TdxHq_API
from pytdx.exhq import TdxExHq_API
from pytdx.params import TDXParams
from pytdx.util.best_ip import select_best_ip
from pytdx.reader import CustomerBlockReader, GbbqReader
from tdx.utils.paths import tdx_path

import pandas as pd
from tdx.utils.memoize import lazyval
from six import PY2

if not PY2:
    from concurrent.futures import ThreadPoolExecutor

from .config import *

SECURITY_BARS_PATCH_NUM1 = 10  # 10 * 800
SECURITY_BARS_PATCH_NUM2 = 26  # 10 * 800
SECURITY_BARS_PATCH_SIZE = 800


def stock_filter(code):
    if code[0] == 1:
        if code[1][0] == '6':
            return True
    else:
        if code[1].startswith("300") or code[1][:2] == '00':
            return True
    return False


class SecurityNotExists(Exception):
    pass


### return 1 if sh, 0 if sz
def get_stock_type(stock):
    one = stock[0]
    if one == '5' or one == '6' or one == '9':
        return 1

    if stock.startswith("009") or stock.startswith("126") or stock.startswith("110") or stock.startswith(
            "201") or stock.startswith("202") or stock.startswith("203") or stock.startswith("204"):
        return 1

    return 0


class Engine:
    def __init__(self, *args, **kwargs):
        if kwargs.pop('best_ip', False):
            self.ip = self.best_ip
        else:
            self.ip = '14.17.75.71'

        self.ip = kwargs.pop('ip', '14.17.75.71')

        self.thread_num = kwargs.pop('thread_num', 1)

        if not PY2 and self.thread_num != 1:
            self.use_concurrent = True
        else:
            self.use_concurrent = False

        self.api = TdxHq_API(args, kwargs)
        if self.use_concurrent:
            self.apis = [TdxHq_API(args, kwargs) for i in range(self.thread_num)]
            self.executor = ThreadPoolExecutor(self.thread_num)

    def connect(self):
        self.api.connect(self.ip)
        if self.use_concurrent:
            for api in self.apis:
                api.connect(self.ip)
        return self

    def __enter__(self):
        return self

    def exit(self):
        self.api.disconnect()
        if self.use_concurrent:
            for api in self.apis:
                api.disconnect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.disconnect()
        if self.use_concurrent:
            for api in self.apis:
                api.disconnect()

    def quotes(self, code):
        code = [code] if not isinstance(code, list) else code
        code = self.security_list[self.security_list.code.isin(code)].index.tolist()
        data = [self.api.to_df(self.api.get_security_quotes(
            code[80 * pos:80 * (pos + 1)])) for pos in range(int(len(code) / 80) + 1)]
        return pd.concat(data)
        # data = data[['code', 'open', 'high', 'low', 'price']]
        # data['datetime'] = datetime.datetime.now()
        # return data.set_index('code', drop=False, inplace=False)

    def stock_quotes(self):
        code = self.stock_list.index.tolist()
        if self.use_concurrent:
            res = {
            self.executor.submit(self.apis[pos % self.thread_num].get_security_quotes, code[80 * pos:80 * (pos + 1)]) \
            for pos in range(int(len(code) / 80) + 1)}
            return pd.concat([self.api.to_df(dic.result()) for dic in res])
        else:
            data = [self.api.to_df(self.api.get_security_quotes(
                code[80 * pos:80 * (pos + 1)])) for pos in range(int(len(code) / 80) + 1)]
            return pd.concat(data)

    @lazyval
    def security_list(self):
        return pd.concat(
            [pd.concat(
                [self.api.to_df(self.api.get_security_list(j, i * 1000)).assign(sse=0 if j == 0 else 1).set_index(
                    ['sse', 'code'], drop=False) for i in range(int(self.api.get_security_count(j) / 1000) + 1)],
                axis=0) for j
                in
                range(2)], axis=0)

    @lazyval
    def stock_list(self):
        aa = map(stock_filter, self.security_list.index.tolist())
        return self.security_list[list(aa)]

    @lazyval
    def best_ip(self):
        return select_best_ip()

    @lazyval
    def concept(self):
        return self.api.to_df(self.api.get_and_parse_block_info(TDXParams.BLOCK_GN))

    @lazyval
    def index(self):
        return self.api.to_df(self.api.get_and_parse_block_info(TDXParams.BLOCK_SZ))

    @lazyval
    def fengge(self):
        return self.api.to_df(self.api.get_and_parse_block_info(TDXParams.BLOCK_FG))

    @lazyval
    def customer_block(self):
        return CustomerBlockReader().get_df(CUSTOMER_BLOCK_PATH)

    @lazyval
    def gbbq(self):
        df = GbbqReader().get_df(GBBQ_PATH).query('category == 1')
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d')
        return df

    def get_security_type(self, code):
        if code in self.security_list.code.values:
            return self.security_list[self.security_list.code == code]['sse'].as_matrix()[0]
        else:
            raise SecurityNotExists()

    def get_security_bars(self, code, freq, index=False):
        if index:
            exchange = self.get_security_type(code)
            func = self.api.get_index_bars
        else:
            exchange = get_stock_type(code)
            func = self.api.get_security_bars

        df = pd.DataFrame()
        if freq in ['1d', 'day']:
            freq = 9
            df = pd.concat(
                [self.api.to_df(func(freq, exchange, code,
                                     (
                                         SECURITY_BARS_PATCH_NUM1 - i - 1) * SECURITY_BARS_PATCH_SIZE,
                                     SECURITY_BARS_PATCH_SIZE)) for i in
                 range(SECURITY_BARS_PATCH_NUM1)]).drop(
                ['year', 'month', 'day', 'hour', 'minute'], axis=1)
            df['datetime'] = pd.to_datetime(df.datetime)
        elif freq in ['1m', 'min']:
            freq = 8
            df = pd.concat(
                [self.api.to_df(
                    func(freq, exchange, code,
                         (SECURITY_BARS_PATCH_NUM2 - i - 1) * SECURITY_BARS_PATCH_SIZE,
                         SECURITY_BARS_PATCH_SIZE)) for i in
                    range(SECURITY_BARS_PATCH_NUM2)]).drop(
                ['year', 'month', 'day', 'hour', 'minute'], axis=1)
            df['datetime'] = pd.to_datetime(df.datetime)
        else:
            print("1d and 1m frequency supported only")
            exit(-1)
        df['code'] = code
        return df.set_index('datetime')


class ExEngine:
    def __init__(self, *args, **kwargs):
        self.api = TdxExHq_API(args, kwargs)

    def connect(self):
        self.api.connect('61.152.107.141', 7727)
        return self

    def __enter__(self):
        return self

    def exit(self):
        self.api.disconnect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.disconnect()

    @lazyval
    def markets(self):
        return self.api.to_df(self.api.get_markets())
