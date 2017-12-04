from pytdx.hq import TdxHq_API
from pytdx.exhq import TdxExHq_API
from pytdx.params import TDXParams
from pytdx.util.best_ip import select_best_ip
from pytdx.reader import CustomerBlockReader, GbbqReader
from tdx.utils.util import fillna
import pandas as pd

import pandas as pd
from tdx.utils.memoize import lazyval
from six import PY2

if not PY2:
    from concurrent.futures import ThreadPoolExecutor

from .config import *


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


if not PY2:
    import queue


    class ConcurrentApi:
        def __init__(self, *args, **kwargs):
            self.thread_num = kwargs.pop('thread_num', 4)
            self.ip = kwargs.pop('ip', '14.17.75.71')
            self.executor = ThreadPoolExecutor(self.thread_num)

            self.queue = queue.Queue(self.thread_num)
            for i in range(self.thread_num):
                api = TdxHq_API(args, kwargs)
                api.connect(self.ip)
                self.queue.put(api)

        def __getattr__(self, item):
            api = self.queue.get()
            func = api.__getattribute__(item)

            def wrapper(*args, **kwargs):
                res = self.executor.submit(func, *args, **kwargs)
                self.queue.put(api)
                return res

            return wrapper


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
                self.executor.submit(self.apis[pos % self.thread_num].get_security_quotes,
                                     code[80 * pos:80 * (pos + 1)]) \
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

    def get_security_bars(self, code, freq, start=None, end=None, index=False):
        if index:
            exchange = self.get_security_type(code)
            func = self.api.get_index_bars
        else:
            exchange = get_stock_type(code)
            func = self.api.get_security_bars

        start = start.tz_localize(None)
        end = end.tz_localize(None)

        if freq in ['1d', 'day']:
            freq = 9
        elif freq in ['1m', 'min']:
            freq = 8
        else:
            raise Exception("1d and 1m frequency supported only")

        res = []
        pos = 0
        while True:
            data = func(freq, exchange, code, pos, 800)
            if not data:
                break
            res = data + res
            pos += 800

            if start and pd.to_datetime(data[0]['datetime']) < start:
                break

        df = self.api.to_df(res).drop(
            ['year', 'month', 'day', 'hour', 'minute'], axis=1)
        df['datetime'] = pd.to_datetime(df.datetime)
        if start:
            df = df.loc[lambda df:start <= df.datetime]
        if end:
            df = df.loc[lambda df:df.datetime < end]
        df['code'] = code
        return df.set_index('datetime')

    def _get_transaction(self, code, date):
        res = []
        start = 0
        while True:
            data = self.api.get_history_transaction_data(get_stock_type(code), code, start, 2000,
                                                         date)
            if not data:
                break
            start += 2000
            res = data + res

        if len(res) == 0:
            return pd.DataFrame()
        df = self.api.to_df(res).assign(date=date)
        df.index = pd.to_datetime(str(date) + " " + df["time"])
        df['code'] = code
        return df.drop("time", axis=1)

    def time_and_price(self, code):
        start = 0
        res = []
        exchange = self.get_security_type(code)
        while True:
            data = self.api.get_transaction_data(exchange, code, start, 2000)
            if not data:
                break
            res = data + res
            start += 2000

        df = self.api.to_df(res)
        df.time = pd.to_datetime(str(pd.to_datetime('today').date()) + " " + df['time'])
        df.loc[0,'time'] = df.time[1]
        return df.set_index('time')

    @classmethod
    def minute_bars_from_transaction(cls, transaction, freq):
        if transaction.empty:
            return pd.DataFrame()
        data = transaction['price'].resample(
            freq, label='right', closed='left').ohlc()

        data['volume'] = transaction['vol'].resample(
            freq, label='right', closed='left').sum()
        data['code'] = transaction['code'][0]

        return fillna(data)

    def get_k_data(self, code, start, end, freq):
        if isinstance(start, str) or isinstance(end, str):
            start = pd.Timestamp(start)
            end = pd.Timestamp(end)
        sessions = pd.date_range(start, end)
        trade_days = map(int, sessions.strftime("%Y%m%d"))

        if freq == '1m':
            freq = '1 min'

        if freq == '1d':
            freq = '24 H'

        res = []
        for trade_day in trade_days:
            df = Engine.minute_bars_from_transaction(self._get_transaction(code, trade_day), freq)
            if df.empty:
                continue
            res.append(df)

        if len(res) != 0:
            return pd.concat(res)
        return pd.DataFrame()


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
