import talib
import pandas as pd
from logbook import Logger

from catalyst.api import (
    order,
    order_target_percent,
    symbol,
    record,
    get_open_orders,
)
from catalyst.utils.run_algo import run_algorithm

algo_namespace = 'korean_rotation'
log = Logger(algo_namespace)


def initialize(context):
    log.info('initializing algo')

    context.etc_usd = symbol('etc_usd')
    context.ltc_usd = symbol('ltc_usd')
    context.xmr_usd = symbol('xmr_usd')
    context.xrp_usd = symbol('xrp_usd')
    context.eth_usd = symbol('eth_usd')
    context.bch_usd = symbol('bch_usd')
    context.dsh_usd = symbol('dsh_usd')

    context.last_rebalance = None
    context.ALLOWANCE_USD = 2000

    context.RSI_BUY_MAX = 40
    context.RSI_SELL_MIN = 70

    context.errors = []
    pass


def _handle_data(context, data):
    this_hour = pd.Timestamp.utcnow().floor('1h')
    if context.last_rebalance is None or this_hour > context.last_rebalance:
        log.debug('rebalancing portfolio')
    else:
        return

    context.last_rebalance = pd.Timestamp.utcnow()
    assets = [
        context.etc_usd,
        context.ltc_usd,
        context.xmr_usd,
        context.xrp_usd,
        context.eth_usd,
        context.bch_usd,
        context.dsh_usd
    ]
    asset_prices = data.history(
        assets,
        fields='price',
        bar_count=60,
        frequency='1h'
    )
    for asset in assets:
        prices = asset_prices[asset]
        rsi = talib.RSI(prices.values, timeperiod=14)[-1]
        macd, signal, hist = talib.MACD(
            prices.values, fastperiod=12, slowperiod=26, signalperiod=9)
        macd_val = macd[-1] - signal[-1]

        log.info('{} rsi: {} macd: {}'.format(asset.symbol, rsi, macd_val))


def handle_data(context, data):
    log.info('handling bar {}'.format(data.current_dt))
    # try:
    _handle_data(context, data)
    # except Exception as e:
    #     log.warn('aborting the bar on error {}'.format(e))
    #     context.errors.append(e)

    log.info('completed bar {}, total execution errors {}'.format(
        data.current_dt,
        len(context.errors)
    ))

    if len(context.errors) > 0:
        log.info('the errors:\n{}'.format(context.errors))


def analyze(context, stats):
    log.info('the full stats:\n{}'.format(stats.head()))
    pass


run_algorithm(
    initialize=initialize,
    handle_data=handle_data,
    analyze=analyze,
    exchange_name='bitfinex',
    live=True,
    algo_namespace=algo_namespace,
    base_currency='usd'
)
