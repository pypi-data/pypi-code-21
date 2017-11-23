from .sub_position import SubPosition


class Position:
    '''
        持仓记录单
    '''

    def __str__(self):
        return "份额：%d (冻结:%d,锁定:%d),现价:%.2f, 均价:%.2f,市值:%.2f,成本:%.2f" % (self._volume, self._frozen_volume,
                                                                         self._locked_volume, self.price,
                                                                         self.avg_cost_price,
                                                                         self.market_value, self._cost)

    def __eq__(self, other):
        if not other:
            return False
        return self._volume == other._volume and self._symbol == other._symbol

    def __init__(self, symbol, volume=0, frozen_volume=0, locked_volume=0, price=0, cost=0):
        self._exchange = ''
        self._symbol = symbol
        self._volume = volume
        self._price = price
        self._frozen_volume = frozen_volume
        self._locked_volume = locked_volume
        self._cost = cost
        self._avg_cost_price = 0 if volume == 0 else cost / volume
        self._subpositions = list()

    def add_position(self, volume, price, locked=False, update_market_price=False):
        p = SubPosition(self._symbol, volume, price)
        self._subpositions.append(p)
        # 记录总量
        self._volume += volume
        # 总成本
        self._cost += volume * price
        # 平均成本
        self._avg_cost_price = self._cost / self._volume
        # 是否锁定
        if locked:
            self._locked_volume += volume
        if update_market_price:
            self._price = price

    def unlock_all_volume(self):
        self._locked_volume = 0

    @property
    def symbol(self):
        return self._symbol

    @property
    def volume(self):
        return self._volume

    @property
    def frozen_volume(self):
        '''
         冻结股份
        '''
        return self._frozen_volume

    def freeze_volume(self, volume):
        '''
         冻结指定数量的股份，卖出操作
        '''
        if self.free_volume < volume:
            return False
        self._frozen_volume += volume
        return True

    def cost_volume(self, volume, price):
        '''
        从冻结扣减股份，卖出成交操作
        '''

        if self._frozen_volume < volume:
            return False
        self.add_position(0 - volume, price, update_market_price=True)
        self._frozen_volume -= volume
        return True

    def release_volume(self, volume):
        '''
        释放冻结的股份
        '''
        if self._frozen_volume < volume:
            return False
        self._frozen_volume -= volume
        return True

    @property
    def cost(self):
        '''
        持有成本
        '''
        return self._cost

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value
        for p in self._subpositions:
            p.price = value
        # 更新市值

    @property
    def avg_cost_price(self):
        '''
        平均成本
        '''
        return self._avg_cost_price

    @property
    def market_value(self):
        '''
         市值
        '''
        return self._price * self._volume

    @property
    def free_volume(self):
        '''
            可操作的股份
        '''
        return self._volume - self._frozen_volume - self._locked_volume

    @property
    def locked_volume(self):
        '''
            锁定的股份
        '''
        return self._locked_volume
