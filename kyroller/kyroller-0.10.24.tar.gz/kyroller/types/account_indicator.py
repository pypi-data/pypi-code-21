

class AccountIndicator:
    def __init__(self):
        self.strategy_id = ''
        self.account_id = ''
        # 净值(cum_inout + cum_pnl + fpnl - cum_commission)
        # 开发中，下面的属性都可修改，后期有些计算属性会变成不可修改的property
        # 下面的字段随时可能修改
        self.net_account_value = 0.0
        self.profit_ratio = 0.0  # 收益率(pnl/cum_inout)
        self.sharp_ratio = 0.0  # 夏普比率
        self.risk_ratio = 0.0  # 风险比率
        self.trade_count = 0  # 交易次数
        self.win_count = 0  # 盈利次数
        self.lose_count = 0  # 亏损次数
        self.win_ratio = 0.0  # 胜率
        self.max_profit = 0.0  # 最大收益
        self.min_profit = 0.0  # 最小收益（最大亏损）
        self.max_single_trade_profit_ratio = 0.0  # 最大单次交易收益率
        self.min_single_trade_profit_ratio = 0.0  # 最小单次交易收益率，也就是最大亏损
        self.max_drawdown = 0.0  # 最大回撤
        self.annual_return = 0.0  # 年化收益率
        self.cum_trade = 0.0  # 累计交易额
        self.cum_pnl = 0.0  # 累计平仓收益(没扣除手续费)
        self.cum_commission = 0.0  # 累计手续费
        self.transact_time = 0.0  # 指标计算时间

    def make_snapshot(self):
        '''
        返回当前快照
        '''
        return self.__dict__.copy()
