import comtypes.client as cc
import comtypes
import time
from enum import Enum
from datetime import datetime
from ..types import *
from ..utils import code_to_symbol, symbol_to_code
import random
import json
from threading import Thread
from events import Events


def print_events(*args):
    print(*args)


class QueryType(Enum):
    STOCKQUERYTYPE_UNKNOWN = 0
    STOCKQUERYTYPE_CAPITAL = 1
    STOCKQUERYTYPE_STOCK = 2
    STOCKQUERYTYPE_TODAYORDER = 3
    STOCKQUERYTYPE_TODAYTRADE = 4
    STOCKQUERYTYPE_TODAYCANREVOKE = 5
    STOCKQUERYTYPE_SHAREHOLDERCODE = 6
    STOCKQUERYTYPE_BALANCEOFFINANCING = 7
    STOCKQUERYTYPE_BORROWFUNDLEFT = 8
    STOCKQUERYTYPE_CANBORROWFUND = 9
    STOCKQUERYTYPE_CAPITALLIST = 10
    STOCKQUERYTYPE_CANNEWSTOCK = 13
    STOCKQUERYTYPE_CANNEWSTOCKLIMIT = 14
    STOCKQUERYTYPE_ASSIGNNUMBER = 15
    STOCKQUERYTYPE_BALLOT = 16


class AccountType(Enum):
    LOGINIACCOUNTTYPE_SZA = 0
    LOGINIACCOUNTTYPE_SHA = 1
    LOGINIACCOUNTTYPE_SZB = 2
    LOGINIACCOUNTTYPE_SHB = 3
    LOGINIACCOUNTTYPE_CAPITAL = 8
    LOGINIACCOUNTTYPE_CUSTOMER = 9
    LOGINIACCOUNTTYPE_THREEBOARD = 12
    LOGINIACCOUNTTYPE_MNCS = 50


class BrokerType(Enum):
    BROKERTYPE_UNKNOWN = 0
    BROKERTYPE_CJZQ = 1
    BROKERTYPE_DYCY = 2
    BROKERTYPE_DGZQ = 3
    BROKERTYPE_GXZQ = 4
    BROKERTYPE_LHZQ = 6
    BROKERTYPE_PAZQ = 7
    BROKERTYPE_GFZQ = 12
    BROKERTYPE_DTZQ = 13
    BROKERTYPE_HXZQ = 14
    BROKERTYPE_XYZQ = 15
    BROKERTYPE_ZSZQ = 16
    BROKERTYPE_JYDT = 17
    BROKERTYPE_ZXJT = 18
    BROKERTYPE_YNHT = 19
    BROKERTYPE_CCZQ = 20
    BROKERTYPE_HYZQ = 21
    BROKERTYPE_GTJA = 22
    BROKERTYPE_SJZQ = 23
    BROKERTYPE_AXZQ = 24
    BROKERTYPE_CFZQ = 25
    BROKERTYPE_DXZQ = 26
    BROKERTYPE_YHZQ = 27
    BROKERTYPE_GDZQ = 28
    BROKERTYPE_YDZQ = 29
    BROKERTYPE_DBZQ = 30
    BROKERTYPE_NJZQ = 31
    BROKERTYPE_ZXZQ = 32
    BROKERTYPE_SHZQ = 33
    BROKERTYPE_HBZQ = 34
    BROKERTYPE_AJZQ = 35
    BROKERTYPE_QLZQ = 36
    BROKERTYPE_ZYGJ = 37
    BROKERTYPE_MZZQ = 38
    BROKERTYPE_XCZQ = 39
    BROKERTYPE_GJZQ = 40
    BROKERTYPE_SCZQ = 41
    BROKERTYPE_GLZQ = 42
    BROKERTYPE_HLZQ = 43
    BROKERTYPE_HFZQ = 44
    BROKERTYPE_GYZQ = 45
    BROKERTYPE_GZZQ = 46
    BROKERTYPE_FZZQ = 47
    BROKERTYPE_BHZQ = 48
    BROKERTYPE_XNZQ = 49
    BROKERTYPE_XSDZQ = 50
    BROKERTYPE_ZTZQ = 51
    BROKERTYPE_HRZQ = 52
    BROKERTYPE_SYWG = 53
    BROKERTYPE_SHXZQ = 54
    BROKERTYPE_JLDB = 56
    BROKERTYPE_MSZQ = 57
    BROKERTYPE_SXDT = 58
    BROKERTYPE_ZCZQ = 59
    BROKERTYPE_XMZQ = 60
    BROKERTYPE_DFZQ = 61
    BROKERTYPE_YTZQ = 62
    BROKERTYPE_JLDT = 67
    BROKERTYPE_WHZQ = 68
    BROKERTYPE_GKZQ = 69
    BROKERTYPE_ZXWT = 70
    BROKERTYPE_XDZQ = 71
    BROKERTYPE_WKZQ = 72
    BROKERTYPE_JHZQ = 73
    BROKERTYPE_HCZQ = 74
    BROKERTYPE_TPYZQ = 75
    BROKERTYPE_GHZQ = 76
    BROKERTYPE_DHZQ = 77
    BROKERTYPE_XBZQ = 78
    BROKERTYPE_SXZQ = 79
    BROKERTYPE_KYZQ = 80
    BROKERTYPE_HAHX = 81
    BROKERTYPE_GSZQ = 83
    BROKERTYPE_ZJZXJT = 84
    BROKERTYPE_SCHX = 85
    BROKERTYPE_WLZQ = 89
    BROKERTYPE_LNZT = 90
    BROKERTYPE_NMHT = 92
    BROKERTYPE_TFZQ = 93
    BROKERTYPE_GSHL = 94
    BROKERTYPE_RXZQ = 95
    BROKERTYPE_ZHZQ = 96
    BROKERTYPE_CTZQ = 98
    BROKERTYPE_HTZQ = 102
    BROKERTYPE_DWZQ = 103
    BROKERTYPE_ZJZS = 104
    BROKERTYPE_LXZQ = 106
    BROKERTYPE_SHHX = 107
    BROKERTYPE_XZTX = 109
    BROKERTYPE_ZYZQ = 110
    BROKERTYPE_BJGD = 111
    BROKERTYPE_ZJZQ = 114
    BROKERTYPE_SXZY = 116
    BROKERTYPE_MNCS = 117
    BROKERTYPE_MNCP = 118
    BROKERTYPE_KT = 996
    BROKERTYPE_DZH = 997
    BROKERTYPE_THS = 998
    BROKERTYPE_TDX = 999


class TdxEventHandle(Events):
    __events_map = {
        '_ITradeEvents_InitEvent': 'on_init',
        '_ITradeEvents_OrderOKEvent': 'on_order_ok',
        '_ITradeEvents_LoginEvent': 'on_login',
        '_ITradeEvents_OrderErrEvent': 'on_order_error',
        '_ITradeEvents_OrderSuccessEvent': 'on_order_success',
        '_ITradeEvents_StockQuoteEvent': 'on_stock_quote',
        '_ITradeEvents_ServerErrEvent': 'on_server_error',
        '_ITradeEvents_ServerChangedEvent': 'on_server_change',
    }

    def __init__(self):
        Events.__init__(self)
        # 初始化事件,events获取一次就会初始化slot
        for e in TdxEventHandle.__events_map.values():
            Events.__getattr__(self, e)

    def __getattr__(self, name):
        if name in TdxEventHandle.__events_map:
            def handler(self, com_obj, *args):
                print(name, *args)
                f = Events.__getattribute__(
                    self, TdxEventHandle.__events_map[name])
                f(*args)
            return comtypes.instancemethod(handler, self, TdxEventHandle)
        else:
            return Events.__getattribute__(self, name)


class TdxAccount(Account, Thread):
    @staticmethod
    def gen_ex_id():
        return datetime.now().strftime('tdx%Y%m%d%H%M%S') + str(random.randrange(1000000, 9999999))

    def __eq__(self, other): return self is other

    def __hash__(self): return hash(id(self))

    def __init__(self, serverIp: str,
                 serverPort: int,
                 authFile,
                 loginId: str,
                 tradePassword: str,
                 tradeAccount: str,
                 brokerType: BrokerType,
                 accountType=AccountType.LOGINIACCOUNTTYPE_CAPITAL,
                 departmentID=0,
                 isCreditAccount=False,
                 enableLog=True,
                 async_login=False):
        Account.__init__(self)
        Thread.__init__(self)
        comtypes.CoUninitialize()
        comtypes.CoInitializeEx(comtypes.COINIT_MULTITHREADED)
        self._com_obj = cc.CreateObject('ZMStockCom.StockTrade')
        self._event_sink = event_sink = TdxEventHandle()
        self._com_event_conn = cc.GetEvents(
            self._com_obj, sink=self._event_sink)
        # con = cc.ShowEvents(self._com_obj)
        self._com_obj.AuthFile = authFile
        self._com_obj.AutoReportSuccess = True
        self._com_obj.CreditAccount = isCreditAccount
        self._com_obj.AutoReportSuccess = True
        self._com_obj.AutoKeepConn = False
        self._com_obj.Init("8.03", 1)
        self._com_obj.EnableLog = enableLog
        self._com_obj.BrokerType = brokerType.value
        self._com_obj.AccountType = accountType.value
        self._com_obj.CurServerHost = serverIp
        self._com_obj.CurServerPort = serverPort
        self._com_obj.LoginID = loginId
        self._com_obj.TradeAccount = tradeAccount
        self._com_obj.DepartmentID = departmentID  # 营业部id
        self._com_obj.TradePassword = tradePassword
        self._logined = False
        print(tradePassword, loginId)
        event_sink.on_login += self._on_login   # pylint: disable=E1101
        event_sink.on_order_success += self._on_order_success  # pylint: disable=E1101

        print('正在登录...')

        loginRet = self._com_obj.Login(async_login)
        # 异步登录
        if not async_login:
            if not loginRet:
                raise Exception(self._com_obj.LastErrDesc)
            else:
                print('开始更新资产信息')
                self.sync_assets()
                self._logined = True

        self.start()

    def _on_order_success(self, tradeRecord):
        dic = json.loads(tradeRecord.GetJsonString())

        pass

    def _on_login(self,  trade_id,  host,  port,  is_ok):
        if not is_ok:
            raise Exception(self._com_obj.LastErrDesc)
        else:
            print('开始更新资产信息')
            self.sync_assets()
            self._logined = is_ok

    def run(self):
        comtypes.CoInitializeEx(comtypes.COINIT_MULTITHREADED)
        while True:
            try:
                cc.PumpEvents(0.1)
            except OSError:
                pass
            except KeyboardInterrupt:
                # ctrl+c 卸载com组件（当前线程）
                comtypes.CoUninitialize()
                break

    def _query_com(self, queryType):
        queryRecord = self._com_obj.queryTradeData(
            self._com_obj.CurTradeId, queryType.value)
        return json.loads(queryRecord.GetJsonString())

    def _wait_for_login(self):
        while not self._logined:
            time.sleep(0.1)

    def sync_assets(self):
        # 获取资金信息
        arrAssets = self._query_com(QueryType.STOCKQUERYTYPE_CAPITAL)
        assert(len(arrAssets) == 1)
        assetsDic = arrAssets[0]
        self._balance = float(assetsDic['可用资金'])
        self._frozen_balance = float(assetsDic['冻结资金'])
        # 获取持仓信息
        arrStocks = self._query_com(QueryType.STOCKQUERYTYPE_STOCK)
        for d in arrStocks:
            symbol = code_to_symbol(d['证券代码'])
            if symbol not in self._positionDic:
                self._positionDic[symbol] = Position(symbol)
            # 可卖数量
            sellableVolume = int(d['可卖数量'])
            allVolume = int(d['库存数量'])
            costPrice = float(d['成本价'])
            if sellableVolume > 0:
                self._positionDic[symbol].add_position(
                    sellableVolume,
                    costPrice,
                    locked=False)
            # 不可卖数量
            if allVolume - sellableVolume > 0:
                self._positionDic[symbol].add_position(
                    allVolume - sellableVolume,
                    costPrice,
                    locked=True)
            self._positionDic[symbol].price = float(d['当前价'])

    def _get_zms_order_type(self, orderType):
        if orderType == OrderType.LIMIT:
            # ORDERPRICETYPE_UNKNOWN
            return 1
        raise TradeError('不支持的交易类型')

    def _get_zms_order_side(self, orderSide):
        if orderSide == OrderSide.BID:
            return 1
        else:
            return 2

    def mk_order(self, order: Order):
        if order.order_type == OrderType.LIMIT:
            if order.price == 0:
                raise TradeError('限价委托必须输入价格')
        if order.order_side == OrderSide.BID:
            need_money = order.price * order.volume
            if self.balance < need_money:
                raise TradeError('用户资金不足')
        elif order.order_side == OrderSide.ASK:
            print(self)
            print(self.get_free_volume_of_symbol(order.symbol))
            if order.volume > self.get_free_volume_of_symbol(order.symbol):
                raise TradeError('可交易份额不足')
        exchange = 0
        # print('同步下单')
        # 同步下单
        # tradeRecord = self._com_obj.SyncCommitOrder(
        #     True,
        #     self._get_zms_order_side(
        #         order.order_side),
        #     self. _get_zms_order_type(
        #         order.order_type),
        #     symbol_to_code(order.symbol),
        #     order.price,
        #     order.volume,
        #     exchange
        # )
        # ret = json.loads(tradeRecord.GetJsonString())
        # print(ret)

        # 异步下单
        # 提交api
        ret = self._com_obj.AddOrder(
            self._get_zms_order_side(order.order_side),
            self. _get_zms_order_type(order.order_type),
            symbol_to_code(order.symbol),
            order.price,
            order.volume,
            exchange
        )
        hret = self._com_obj.CommitOrder(self._com_obj.CurTradeId, 0, 2)
        print(exchange, ret, hret)
        self._register_order(order)
