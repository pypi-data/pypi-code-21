from ocean.fishes.trade import *

class Portfolio:
    """
    This class contains the information
    about a portfolio
    """

    def __init__(self):
        self.longs = {}
        self.closed_longs = {}
        self.shorts = {}
        self.closed_shorts = {}
        self.max_portfolio_size = 50000
        self.value_per_trade = 10000
        self.use_optimal_f = False
        self.f = 1.0
        self.position_sizing = False
        self.position_sizing_type = ''
        self.positive_trades = 0
        self.total_trades = 0
        self.prev_trade = None
        self.max_consecutive_loss = 0
        self.consecutive_loss = 0
        self.gain = 0
        self.pain = 0
        self.transaction_cost = 0.0003
        self.daily_df = pd.DataFrame(
            columns=[
                'long_pl',
                'short_pl',
                'long_exposure',
                'short_exposure',
                'num_longs',
                'num_shorts'])

    def track_stats(self, pos):
        """
        upon closing a trade we record the PL and
        other records related to trades
        """
        if pos.total_pl < 0:
            if self.prev_trade is None or self.prev_trade == 'loss':
                self.consecutive_loss += 1
            else:
                self.consecutive_loss = 1
            self.max_consecutive_loss = max(
                self.consecutive_loss, self.max_consecutive_loss)
            self.pain += pos.total_pl
            self.prev_trade = 'loss'

        elif pos.total_pl > 0:
            self.positive_trades += 1
            self.gain += pos.total_pl
            self.prev_trade = 'profit'

    def go_long(self, px, date, atr):
        """
        start new long position
        """
        trade = Trade()
        profit_till_date = self.daily_df.long_pl.sum()
        profit_till_date += self.daily_df.short_pl.sum()
        portfolio_size = profit_till_date + self.max_portfolio_size
        if not self.use_optimal_f and not self.position_sizing:
            entry_value = self.value_per_trade
        elif self.position_sizing:
            # if percent volatility - positions based on volatiity
            if self.position_sizing_type == 'percent_volatility':
                entry_value = self.value_per_trade / atr
            # if market money - chose 25% of profits
            if self.position_sizing_type == 'market_money':
                entry_value = self.value_per_trade + \
                    max(0, profit_till_date) * 0.25
            # if multi tier - increase entry value if profit increases
            if self.position_sizing_type == 'multi_tier':
                if profit_till_date > 0:
                    profit_perc = int(
                        profit_till_date / self.value_per_trade / 5)
                    entry_value = self.value_per_trade * (1 + profit_perc)
                else:
                    entry_value = self.value_per_trade
        elif self.use_optimal_f:
            entry_value = max(
                0,
                self.f *
                self.value_per_trade +
                profit_till_date)
        entry_value = max(0, min(portfolio_size, entry_value))
        trade.initiate_trade(entry_value, px, 'long', date)
        self.longs[date] = trade
        self.total_trades += 1

    def go_short(self, px, date, atr):
        """
        start new short position
        """
        trade = Trade()
        profit_till_date = self.daily_df.long_pl.sum()
        profit_till_date += self.daily_df.short_pl.sum()
        portfolio_size = profit_till_date + self.max_portfolio_size
        if not self.use_optimal_f or not self.position_sizing:
            entry_value = self.value_per_trade
        elif self.position_sizing:
            # if percent volatility - positions based on volatiity
            if self.position_sizing_type == 'percent_volatility':
                entry_value = self.value_per_trade / atr
            # if market money - chose 25% of profits
            if self.position_sizing_type == 'market_money':
                entry_value = self.value_per_trade + \
                    max(0, profit_till_date) * 0.25
            # if multi tier - increase entry value if profit increases
            if self.position_sizing_type == 'multi_tier':
                if profit_till_date > 0:
                    profit_perc = int(
                        profit_till_date / self.value_per_trade / 5)
                    entry_value = self.value_per_trade * (1 + profit_perc)
                else:
                    entry_value = self.value_per_trade
        elif self.use_optimal_f:
            entry_value = max(
                0,
                self.f *
                self.value_per_trade +
                profit_till_date)
        entry_value = max(0, min(portfolio_size, entry_value))
        trade.initiate_trade(entry_value, px, 'short', date)
        self.shorts[date] = trade
        self.total_trades += 1

    def pyramid_long(self, px, date, pyramid_type):
        """
        pyramid a long position using upright
        pyramiding
        """
        profit_till_date = self.daily_df.long_pl.sum()
        profit_till_date += self.daily_df.short_pl.sum()
        portfolio_size = profit_till_date + self.max_portfolio_size

        for l in self.longs.keys():
            pos = self.longs[l]
            pos.increase += 1
            # if upright pyramid - keep adding halfof last addition
            if pyramid_type == 'upright':
                add_value = pos.starting_value / pow(2, pos.increase)
            # if inverted pyramid - add equal weights
            elif pyramid_type == 'inverted':
                if pos.increase < 5:
                    add_value = pos.starting_value
                else:
                    add_value = 0
            # if reflective pyramid - add and then decrease positions
            elif pyramid_type == 'reflecting':
                mult = 1
                if pos.increase == 1:
                    mult = 0.5
                elif pos.increase == 2:
                    mult = 0.2
                elif pos.increase == 3:
                    mult = -0.2
                elif pos.increase == 4:
                    mult = -0.5
                elif pos.increase == 5:
                    mult = -1.0
                else:
                    mult = 0
                add_value = pos.starting_value * mult
            # cap addition by max portfolio value
            free_capital = portfolio_size - pos.current_value
            add_value = max(0, min(free_capital, add_value))
            # add transaction cost
            add_value *= (1 - self.transaction_cost)
            add_shares = add_value / px
            if pos.shares + add_shares > 0:
                pos.entry_px = (px * add_shares + pos.entry_px *
                                pos.shares) / (pos.shares + add_shares)
            pos.entry_value += add_value
            pos.shares += add_shares

    def pyramid_short(self, px, date, pyramid_type):
        """
        pyramid a short position using upright
        pyramiding
        """
        profit_till_date = self.daily_df.long_pl.sum()
        profit_till_date += self.daily_df.short_pl.sum()
        portfolio_size = profit_till_date + self.max_portfolio_size
        for l in self.shorts.keys():
            pos = self.shorts[l]
            pos.increase += 1
            # if upright pyramid - keep adding halfof last addition
            if pyramid_type == 'upright':
                add_value = pos.starting_value / pow(2, pos.increase)
            # if inverted pyramid - add equal weights
            elif pyramid_type == 'inverted':
                if pos.increase < 5:
                    add_value = pos.starting_value
                else:
                    add_value = 0
            # if reflective pyramid - add and then decrease positions
            elif pyramid_type == 'reflecting':
                mult = 1
                if pos.increase == 1:
                    mult = 0.5
                elif pos.increase == 2:
                    mult = 0.2
                elif pos.increase == 3:
                    mult = -0.2
                elif pos.increase == 4:
                    mult = -0.5
                elif pos.increase == 5:
                    mult = -1.0
                else:
                    mult = 0
                add_value = pos.starting_value * mult
            # cap addition by max portfolio value
            free_capital = portfolio_size - pos.current_value
            add_value = max(0, min(free_capital, add_value))
            # add transaction cost
            add_value *= (1 - self.transaction_cost)
            add_shares = add_value / px
            if (pos.shares + add_shares) > 0:
                pos.entry_px = (px * add_shares + pos.entry_px *
                                pos.shares) / (pos.shares + add_shares)
            pos.entry_value += add_value
            pos.shares += add_shares

    def exit_long(self, px, date):
        """
        exit an active long position
        """
        rem = []
        for l in self.longs.keys():
            pos = self.longs[l]
            pos.close_position(date)
            self.track_stats(pos)
            rem.append(l)
        for r in rem:
            self.closed_longs[r] = self.longs[r]
            self.longs.pop(r)

    def exit_short(self, px, date):
        """
        exit an active short position
        """
        rem = []
        for l in self.shorts.keys():
            pos = self.shorts[l]
            pos.close_position(date)
            self.track_stats(pos)
            rem.append(l)
        for r in rem:
            self.closed_shorts[r] = self.shorts[r]
            self.shorts.pop(r)

    def calculate_value(self, px, date):
        """
        calculate and record portfolio value
        """
        long_pl = 0
        long_value = 0
        short_pl = 0
        short_value = 0
        for l in self.longs.keys():
            pos = self.longs[l]
            pos.calc_current_value(px)
            long_pl += pos.today_pl
            long_value += pos.current_value
        for l in self.shorts.keys():
            pos = self.shorts[l]
            pos.calc_current_value(px)
            short_pl += pos.today_pl
            short_value += pos.current_value
        self.daily_df.loc[date,
                          :] = [long_pl,
                                short_pl,
                                long_value,
                                short_value,
                                len(self.longs),
                                len(self.shorts)]