from zipline.assets import Equity
from zipline.algorithm import TradingAlgorithm
from zipline.utils.memoize import lazyval
from zipline.finance.controls import (
    LongOnly
)
from cn_zipline.finance.controls import LimitPrice


def get_round_lot(asset):
    # fixme 131810
    assert isinstance(asset, Equity)
    return 100


class CnTradingAlgorithm(TradingAlgorithm):
    def __init__(self, *args, **kwargs):
        super(CnTradingAlgorithm, self).__init__(*args, **kwargs)

        self.trading_controls = [LongOnly(on_error="log"), LimitPrice(on_error='log')]

    def _calculate_order_value_amount(self, asset, value):
        amount = super(CnTradingAlgorithm, self)._calculate_order_value_amount(asset, value)
        round_lot = get_round_lot(asset)
        if isinstance(asset, Equity):
            amount = int(amount / round_lot) * round_lot
        return amount
