class ExecutionRpt:
    '''
    成交回报
    '''

    def __str__(self):
        return 'order:%s side:%s symbol:%s volume:%d price:%.2f amount:%.2f' % (
            self.order_cid, self.side, self.symbol, self.volume, self.price, self.amount
        )

    def __init__(self, order_cid, symbol,  order_side, volume, price, timestamp):
        self.order_cid = order_cid
        self.side = order_side
        self.symbol = symbol
        self.volume = volume
        self.price = price
        self.amount = price * volume
        self.timestamp = timestamp
