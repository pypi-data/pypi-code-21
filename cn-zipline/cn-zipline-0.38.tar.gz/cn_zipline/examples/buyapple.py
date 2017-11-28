# coding=utf-8

from zipline.api import order, record, symbol


def initialize(context):
    context.smb = symbol('000001')


def handle_data(context, data):
    can_trade = data.can_trade(context.smb)
    if can_trade:
        order(context.smb, 10)
        current_dt = data.current_dt
        open = data.current(context.smb,'open')
        high = data.current(context.smb, 'high')
        low = data.current(context.smb, 'low')
        close = data.current(context.smb, 'close')
        volume = data.current(context.smb, 'volume')
        price = data.current(context.smb,'price')

        record(price=data.current(context.smb, 'price'))


if __name__ == '__main__':
    from zipline.utils.cli import Date
    from cn_stock_holidays.zipline.default_calendar import shsz_calendar
    from cn_zipline.utils.run_algo import run_algorithm

    start = Date(tz='utc', as_timestamp=True).parser('2017-10-15')

    end = Date(tz='utc', as_timestamp=True).parser('2017-11-01')

    run_algorithm(start, end, initialize, 10e6, handle_data=handle_data, bundle='tdx',trading_calendar=shsz_calendar,data_frequency="daily", output='out.pickle')
    # run_algorithm(start, end, initialize, 10e6, handle_data=handle_data)
