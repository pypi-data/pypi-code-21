import pandas as pd

from catalyst.api import symbol
from catalyst.utils.run_algo import run_algorithm


def initialize(context):
    context.asset = symbol('btc_usdt')


def handle_data(context, data):
    pass


def analyze(context=None, results=None):
    pass


start = pd.to_datetime('2017-11-1', utc=True)
end = pd.to_datetime('2017-11-3', utc=True)
results = run_algorithm(initialize=initialize,
                        handle_data=handle_data,
                        analyze=analyze,
                        start=start,
                        end=end,
                        exchange_name='poloniex',
                        capital_base=100000,
                        data_frequency='minute')
