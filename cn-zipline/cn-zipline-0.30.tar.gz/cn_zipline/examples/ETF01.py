# coding=utf-8

from zipline.api import order, record, symbol, schedule_function, order_target_percent
from zipline.api import date_rules
from cn_zipline.utils.run_algo import run_algorithm
from zipline.utils.cli import Date
from cn_stock_holidays.zipline.default_calendar import shsz_calendar
import pandas as pd
import logging


def initialize(context):
    context.stocks = [symbol("518880"),
                      symbol("513500"),
                      symbol("513100"),
                      symbol("513050"),
                      symbol("513030"),
                      symbol("512880"),
                      symbol("512660"),
                      symbol("512580"),
                      symbol("512400"),
                      symbol("512200"),
                      symbol("511010"),
                      symbol("510500"),
                      symbol("510300"),
                      symbol("510050"),
                      symbol("502013"),
                      symbol("162411"),
                      symbol("161631"),
                      symbol("159939"),
                      symbol("159938"),
                      symbol("159928"),
                      symbol("159920"),
                      symbol("159915"),
                      symbol("159902")]
    context.LOOKBACK = 5
    context.OBSERVATION = 30
    # update_universe(context.stocks)
    schedule_function(rebalance, date_rule=date_rules.every_day())


def rebalance(context, data):
    historydata = data.history(context.stocks, bar_count=context.OBSERVATION, frequency='1d', fields='close')
    toplist = getTopSectors(historydata, context.stocks, context.LOOKBACK)
    stocklist = toplist

    for stock in context.portfolio.positions:
        if stock not in stocklist:
            order_target_percent(stock, 0)

    weight = update_weights(context, stocklist)

    for stock in stocklist:
        if weight != 0:
            order_target_percent(stock, weight)


def getStockPerformance(price, period):
    start = price[-period]  # start price
    end = price[-1]  # end price

    performance = (end - start) / start
    return performance


def getTopSectors(price, stocks, period):
    stock_index = []
    stock_return = []

    for stock in stocks:
        stock_index.append(stock)
        performance = getStockPerformance(price[stock].values, period)
        stock_return.append(performance)

    data = pd.DataFrame(stock_return, index=stock_index, columns=['price_return'])
    data = data.sort(['price_return'], ascending=[0])
    stocklist = data.head(10).index.values

    logging.info("selected stock:")
    logging.info(stocklist)

    return stocklist


def update_weights(context, stocks):
    if len(stocks) == 0:
        return 0
    else:

        weight = .98 / len(stocks)
        return weight


def handle_data(context, data):
    pass


if __name__ == '__main__':
    start = Date(tz='utc', as_timestamp=True).parser('2017-10-01')

    end = Date(tz='utc', as_timestamp=True).parser('2017-11-07')
    run_algorithm(start, end, initialize, 10e6, handle_data=handle_data, bundle='tdx', trading_calendar=shsz_calendar,
                  data_frequency="daily", output='out.pickle')
