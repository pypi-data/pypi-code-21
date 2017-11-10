from zipline.assets import Equity
from zipline.algorithm import TradingAlgorithm
from zipline.utils.memoize import lazyval


@lazyval
def get_round_lot(asset):
    # fixme 131810
    assert isinstance(asset, Equity)
    return 100


def _calculate_order_value_amount(cls, asset, value):
    amount = cls._old_calculate_order_value_amount(asset, value)
    round_lot = get_round_lot(asset)
    if isinstance(asset, Equity):
        amount = int(amount / round_lot) * round_lot
    return amount


TradingAlgorithm._old_calculate_order_value_amount = TradingAlgorithm._calculate_order_value_amount
TradingAlgorithm._calculate_order_value_amount = _calculate_order_value_amount
