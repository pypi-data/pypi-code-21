from zipline.algorithm_live import LiveTradingAlgorithm
from zipline.finance.controls import (
    LongOnly
)
from zipline.assets import Equity
from cn_zipline.finance.controls import LimitPrice
from cn_zipline.algorithm import get_round_lot


# TODO can't use inherit, cause bugs https://stackoverflow.com/questions/32831150/maximum-recursion-depth-error-in-python-when-calling-supers-init

def __init__(self, *args, **kwargs):
    self._orig__init__(*args, **kwargs)
    self.trading_controls = [LongOnly(on_error="log"), LimitPrice(on_error='log')]


def _calculate_order_value_amount(self, asset, value):
    amount = self._orig_calculate_order_value_amount(asset, value)
    round_lot = get_round_lot(asset)
    if isinstance(asset, Equity):
        amount = int(amount / round_lot) * round_lot


CnLiveTradingAlgorithm = LiveTradingAlgorithm
setattr(CnLiveTradingAlgorithm, "_orig_calculate_order_value_amount",
        CnLiveTradingAlgorithm._calculate_order_value_amount)
setattr(CnLiveTradingAlgorithm, "_orig__init__",
        CnLiveTradingAlgorithm.__init__)
setattr(CnLiveTradingAlgorithm, "__init__", __init__)
setattr(CnLiveTradingAlgorithm, '_calculate_order_value_amount', _calculate_order_value_amount)
