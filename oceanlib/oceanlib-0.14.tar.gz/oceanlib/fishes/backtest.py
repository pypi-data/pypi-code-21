from ocean.fishes.portfolio import *

class Backtest:
    """
    this class defines a backtest
    """

    def __init__(self, prices, pyramid_type, position_sizing_type):
        """
        class constructor
        """
        self.prices = prices
        self.pyramid = True
        self.pyramid_type = pyramid_type
        self.position_sizing = True
        self.position_sizing_type = position_sizing_type
        self.portfolio = Portfolio()
        self.portfolio.position_sizing = self.position_sizing
        self.portfolio.position_sizing_type = self.position_sizing_type
        self.end_date = max(prices.index)

    def long_signal(self, i):
        """
        if long signal triggered
        """
        if self.prices.loc[i,
                           'close'] < self.prices.loc[i,
                                                      'ema'] - self.prices.loc[i,
                                                                               'atr']:
            return True
        return False

    def short_signal(self, i):
        """
        if short signal triggered
        """
        if self.prices.loc[i,
                           'close'] > self.prices.loc[i,
                                                      'ema'] + self.prices.loc[i,
                                                                               'atr']:
            return True
        return False

    def exit_long_signal(self, i):
        """
        if exit long signal triggered
        """
        if self.prices.loc[i, 'close'] >= self.prices.loc[i, 'ema']:
            return True
        if i == self.end_date:
            return True
        return False

    def exit_short_signal(self, i):
        """
        if exit short signal triggered
        """
        if self.prices.loc[i, 'close'] <= self.prices.loc[i, 'ema']:
            return True
        if i == self.end_date:
            return True
        return False

    def backtest(self):
        """
        the backtest code
        """
        for i in self.prices.index:
            px = self.prices.loc[i, 'close']
            vol = self.prices.loc[i, 'atr']
            self.portfolio.calculate_value(px, i)
            num_longs = len(self.portfolio.longs)
            num_shorts = len(self.portfolio.shorts)
            if self.long_signal(i):
                if num_longs + num_shorts == 0:
                    # if no positions and long triggered - go long
                    self.portfolio.go_long(px, i, vol)
                elif self.pyramid and num_longs > 0:
                    # if long position and long triggered - pyramid
                    self.portfolio.pyramid_long(px, i, self.pyramid_type)
            elif self.short_signal(i):
                if num_longs + num_shorts == 0:
                    # if no positions and short triggered - go short
                    self.portfolio.go_short(px, i, vol)
                elif self.pyramid and num_shorts > 0:
                    # if short position and short triggered - pyramid
                    self.portfolio.pyramid_short(px, i, self.pyramid_type)
            elif num_longs > 0 and self.exit_long_signal(i):
                # if exit long triggered - exit
                self.portfolio.exit_long(px, i)
            elif num_shorts > 0 and self.exit_short_signal(i):
                # if exit short triggered - exit
                self.portfolio.exit_short(px, i)
        self.portfolio.daily_df['daily_pl'] = self.portfolio.daily_df['long_pl'] + \
            self.portfolio.daily_df['short_pl']

    def analyse(self):
        df = self.portfolio.daily_df
        df['daily_pl'] = df['long_pl'] + df['short_pl']
        # calculate cumulative PL
        df['cum_pl'] = df['daily_pl'].cumsum()
        portfolio_size = 50000

        # total number of trades
        num_trades = self.portfolio.total_trades
        # positive trades
        positive_trades = self.portfolio.positive_trades
        PLR = (self.portfolio.gain / positive_trades)
        PLR /= abs(self.portfolio.pain / (num_trades - positive_trades))
        p = positive_trades / num_trades
        f = (p * (PLR + 1) - 1) / PLR
        # wining percentage
        win_perc = positive_trades / num_trades
        # win to loss ratio
        if num_trades - positive_trades > 0:
            winloss = positive_trades / (num_trades - positive_trades)
        else:
            winloss = np.inf
        # return per trade
        ret_per_trade = df.daily_pl.sum() / num_trades / portfolio_size
        # calculate Max consecutive loss
        max_cons_loss = self.portfolio.max_consecutive_loss
        # calaulte max drawdown
        s = df.cum_pl + portfolio_size
        drawdown = 1 - s / s.cummax()
        mdd = -1 * drawdown.max()
        # calculate CAGR - annualize average daily return
        periods = (df.index[-1] - df.index[0]).days / 365
        last = df.loc[df.index[-1], 'cum_pl'] + portfolio_size
        first = portfolio_size
        cagr = (last / first)**(1 / periods) - 1
        # calculate lake ratio
        p = s.cummax()
        water = sum(p - s)
        earth = sum(s)
        lake_ratio = water / earth
        # calculate gain to pain ratio
        if self.portfolio.pain != 0:
            gain_to_pain = self.portfolio.gain / abs(self.portfolio.pain)
        else:
            gain_to_pain = np.inf
        # tabulate reults
        output = pd.DataFrame(columns=['value'])
        output.loc['Win %', 'value'] = win_perc * 100
        output.loc['Num Trades', 'value'] = num_trades
        output.loc['Win to Loss Ratio', 'value'] = winloss
        output.loc['Mean Return Per Trade %', 'value'] = ret_per_trade * 100
        output.loc['Max Consecutive Losers', 'value'] = max_cons_loss
        output.loc['Max Drawdown %', 'value'] = mdd * 100
        output.loc['CAGR %', 'value'] = cagr * 100
        output.loc['Lake Ratio', 'value'] = lake_ratio
        output.loc['Gain to Pain Ratio', 'value'] = gain_to_pain
        output.loc['Optimal F', 'value'] = f
        return output