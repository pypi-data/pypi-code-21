from .types import *
import random
from datetime import datetime
from termcolor import *
from .apis import TradeApi


class Strategy(AccountListener):
    __strategy_index = 0

    def __init__(self, id=None, output=None, api=None):
        index = Strategy.__strategy_index
        Strategy.__strategy_index += 1
        # 初始化余额
        self._api = api
        self._output = output
        self._state = State()
        self._account = None
        self._timestamp = 0
        if id is not None:
            self._id = id
        else:
            self._id = "%s#%d" % (type(self).__name__, index)

    def log(self, message, color, level):
        message = message if isinstance(message, str) else str(message)
        t = datetime.now().strftime('%H:%M:%S')
        if(self._output):
            self._output.write(
                '<p class="color_%s level_%s">%s</p>' % (color, level, message))
        else:
            msg = self.id + ' ' + t + ' : ' + message
            print(colored(msg, color))

    def print(self, message, color='white', level=5):
        self.log(message, color, level)

    def record(self):
        pass

    def format_timestamp(self, timestamp, format='%Y-%m-%d %H:%M:%S'):
        return datetime.fromtimestamp(timestamp).strftime(format)

    @property
    def id(self):
        return self._id

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, value):
        self._api = value

    @property
    def account(self) -> Account:
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def state(self):
        return self._state

    def reset_state(self):
        '''
        如果需要重复运行，使用这个初始化所有状态
        '''
        self.print('reset_state', 'red')
        self._state = State()

    def cancel_order(self, order_cid):
        return self._account.calcel_order(order_cid)

    def mk_order(self, symbol, order_side, volume,  price=0, order_type=None):
        order = Order()
        order.order_side = order_side
        order.volume = volume
        order.price = price
        order.symbol = symbol
        order.strategy_id = self.id
        if order_type is None:
            if price != 0:
                order.order_type = OrderType.LIMIT
            else:
                raise Exception('not defined order_type')
        else:
            order.order_type = order_type
        # self.print('mk_order:( %s)' % str(order))
        return self._account.mk_order(order)

    def init(self, subs, start_time=None, end_time=None):
        pass

    def prepare(self, subs, start_time=None, end_time=None):
        ''' 初始化
            symbols: 订阅的相关股票代码（避免多余的初始化）
            start_time: 回测的时候用，传入回测时间戳，实盘模式将为当前时间
        '''
        self.print('\t account: (%s)' % str(self.account), 'yellow')
        self.print('\t care of subs: ( %s )' % subs, 'yellow')
        if start_time is not None:
            if end_time is not None:
                self.print('\t in backtest mode, from %s to %s ' %
                           (self.format_timestamp(start_time), self.format_timestamp(end_time)), 'yellow')
            else:
                self.print('\t in backtest mode, from  %s ' %
                           (self.format_timestamp(start_time)), 'yellow')
        self.init(subs, start_time=None, end_time=None)

    def handle_order_status_cahnge(self, order, src_status: OrderStatus):
        self.on_order_status_changed(order, src_status)
        if order.status == OrderStatus.CONFIRMED:  # 订单被确认
            self.on_order_confirmed(order, src_status)
        elif order.status == OrderStatus.PART_FILLED:  # 订单被交易
            self.on_order_traded(order, src_status)
        elif order.status == OrderStatus.ALL_FILLED:  # 订单被全部交易
            self.on_order_traded(order, src_status)
        elif order.status == OrderStatus.PART_CANCELED:  # 订单部分取消
            self.on_order_canceled(order, src_status)
        elif order.status == OrderStatus.CANCELED:   # 订单被取消
            self.on_order_canceled(order, src_status)
        elif order.status == OrderStatus.REJECTED:   # 订单被拒绝
            self.on_order_rejected(order, src_status)

    def handle_exerpt(self, rpt):
        self.on_exerpt(rpt)
        pass

    def on_exerpt(self, rpt):
        pass

    def handle_tick(self, tick):
        self._timestamp = tick.timestamp
        self.on_tick(tick)

    def handle_bar(self, bar):
        self._timestamp = bar.timestamp
        self.on_bar(bar)

    def handle_market_event(self, e):
        self._timestamp = e.timestamp
        self.on_market_event(e)

    def handle_deal(self, e):
        self.on_deal(e)

    def on_market_event(self, e: MarketEvent):
        print(e)
        pass

    def on_tick(self, tick):
        print(tick)
        pass

    def on_bar(self, tick):
        print(tick)
        pass

    def on_deal(self, tick):
        print(tick)
        pass

    def on_order_canceled(self, order, src_status):
        '''
        委托单被撤单成功
        '''
        self.print(str(order) +
                   ' has been canceld', 'red', 0)

    def on_order_rejected(self, order, src_status):
        '''
        委托单被拒绝，开单失败
        '''
        self.print(str(order) +
                   ' has been canceld', 'red', 0)

    def on_order_traded(self, order, src_status):
        '''
        委托单有产生交易
        '''
        self.print(str(order) +
                   ' has been trade:', 'red', 0)

    def on_order_confirmed(self, order, src_status):
        '''
         委托单被确认
        '''
        self.print(str(order) +
                   ' has been confirmed:', 'red', 0)

    def on_order_status_changed(self, order, src_status):
        pass

    def handle_events(self, _type, msg):
        if _type == 'tick' or _type == 'quotation':
            self.handle_tick(msg)
        elif _type == 'bar':
            self.handle_bar(msg)
        elif _type == 'market':
            self.handle_market_event(msg)
        elif _type == 'deal':
            self.handle_deal(msg)
