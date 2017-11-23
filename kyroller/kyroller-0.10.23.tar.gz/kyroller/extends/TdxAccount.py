from datetime import datetime
from ..types import *
import random


class TdxAccount(Account):

    def __init__(self, balance, frozen_balance=0, positions=None, bid_fee_radio=0, ask_fee_radio=0, transection_radio=1):
        Account.__init__(self, balance, frozen_balance,
                         positions, bid_fee_radio, ask_fee_radio)
        self._price_map = {}
        self._transection_radio = transection_radio

    @staticmethod
    def gen_ex_id():
        return datetime.now().strftime('tdx%Y%m%d%H%M%S') + str(random.randrange(1000000, 9999999))

    def _change_order_status(self, order: Order, dst_status: OrderStatus):
        '''
        改变订单状态
        '''
        src_status = order.status
        order.status = dst_status
        # 触发订单事件
        if self._order_change_callback is not None:
            self._order_change_callback(order, src_status)

    def _register_order(self, order):
        order.ex_id = TdxAccount.gen_ex_id()
        self._orders.append(order)

    def mk_order(self, order: Order):
        pass

    def cancel_order(self, order_cid):
        pass

    def _try_trade(self, symbol, price, timestamp):
        pass

    def handle_bar(self, bar: Bar):
        pass

    def handle_tick(self, tick: Tick):
        pass

    def handle_market_event(self, e: MarketEvent):
        pass

    def handle_events(self, _type, msg):
        pass
