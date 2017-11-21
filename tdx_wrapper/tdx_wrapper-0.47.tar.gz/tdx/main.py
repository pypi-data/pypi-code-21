# -*- coding:utf-8 –*-

from tdx.engine import Engine
import datetime
from tdx.utils.util import precise_round
import pandas as pd
import click


def process_quotes(quotes):
    quotes['change'] = quotes['price'] / quotes['last_close'] - 1
    quotes['up_limit'] = (quotes['last_close'] * 1.1).apply(precise_round) == quotes['price']
    quotes['down_limit'] = (quotes['last_close'] * 0.9).apply(precise_round) == quotes['price']
    quotes.sort_values('change', ascending=False, inplace=True)
    quotes.set_index('code', drop=False, inplace=True)
    block = pd.concat([engine.concept, engine.index, engine.fengge])
    quotes = block.set_index('code').join(quotes, how='inner')
    grouped = quotes.groupby('blockname').sum()[['up_limit', 'down_limit', 'amount']]
    print(grouped.sort_values('up_limit', ascending=False))


def test_minute_time_data():
    stock_list = engine.stock_list.index.tolist()

    now = datetime.datetime.now()

    for stock in stock_list:
        fs = engine.api.to_df(engine.api.get_minute_time_data(stock[0], stock[1]))
        # print(fs)

    print((datetime.datetime.now() - now).total_seconds())


def test_quotes():
    start_dt = datetime.datetime.now()
    quote = engine.stock_quotes()
    print(datetime.datetime.now() - start_dt).total_seconds()
    process_quotes(quote)


if __name__ == '__main__':
    engine = Engine(auto_retry=True, multithread=True, thread_num=8)
    with engine.connect():

        start = '20171001'
        end = '20171010'
        code = '000001'
        time = datetime.datetime.now()
        print(engine.get_k_data(code,start,end,"1min"))
        print((datetime.datetime.now()  - time).total_seconds())


        # with click.progressbar(timestamp2int(sessions),
        #                        item_show_func=lambda e: e if e is None else str(e[0])
        #                        ) as date:
        #     print(engine.get_transaction('000001', date))

        # test_quotes()
        # print(engine.get_security_bars('513500','1d'))

