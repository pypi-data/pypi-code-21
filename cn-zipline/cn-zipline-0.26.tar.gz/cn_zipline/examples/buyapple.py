# coding=utf-8

from zipline.api import order, record, symbol


def initialize(context):
    pass


def handle_data(context, data):
    can_trade = data.can_trade(symbol('000001'))
    if can_trade:
        order(symbol('000001'), 10)
        current_dt = data.current_dt
        open = data.current(symbol('000001'),'open')
        high = data.current(symbol('000001'), 'high')
        low = data.current(symbol('000001'), 'low')
        close = data.current(symbol('000001'), 'close')
        volume = data.current(symbol('000001'), 'volume')
        price = data.current(symbol('000001'),'price')

        record(AAPL=data.current(symbol('000001'), 'price'))


if __name__ == '__main__':
    from cn_zipline.utils.run_algo import run_algorithm
    from zipline.utils.cli import Date
    from cn_stock_holidays.zipline.default_calendar import shsz_calendar

    start = Date(tz='utc', as_timestamp=True).parser('2017-10-15')

    end = Date(tz='utc', as_timestamp=True).parser('2017-11-01')
    run_algorithm(start, end, initialize, 10e6, handle_data=handle_data, bundle='tdx',trading_calendar=shsz_calendar,data_frequency="minute", output='out.pickle')
