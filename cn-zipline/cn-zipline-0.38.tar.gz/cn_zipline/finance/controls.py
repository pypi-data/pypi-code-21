from zipline.finance.controls import TradingControl
from zipline.assets import Equity


class LimitPrice(TradingControl):
    """
    Do not order if for limit price
    """

    def __init__(self, on_error):
        super(LimitPrice, self).__init__(on_error)

    def validate(self,
                 asset,
                 amount,
                 portfolio,
                 algo_datetime,
                 algo_current_data):
        """
        Fail if long when limit up or shot when limit down.
        """

        if isinstance(asset, Equity):
            current_price = algo_current_data.current(asset, "price")
            pre_close = algo_current_data.history(asset, bar_count=2, fields='close', frequency="1d")[0]

            if amount > 0:
                limit_up = round(pre_close + 1.1, 2)
                if current_price == limit_up:
                    self.handle_violation(asset, amount, algo_datetime)
            else:
                limit_down = round(pre_close * 0.9, 2)
                if current_price == limit_down:
                    self.handle_violation(asset, amount, algo_datetime)


class T1Trade(TradingControl):
    def __init__(self, on_error):
        super(T1Trade, self).__init__(on_error)

    def validate(self,
                 asset,
                 amount,
                 portfolio,
                 algo_datetime,
                 algo_current_data):
        """
        Fail if buy and sell on the same day
       """

        if isinstance(asset, Equity):
            pass
