# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals


# 基本api
from gm import __version__
from gm.enum import *

from gm.csdk.c_sdk import py_gmi_set_version
from .basic import (
    set_token, get_version, subscribe, unsubscribe,
    current, get_strerror, schedule, run, set_parameter,
    add_parameter, log, set_serv_addr, stop)

# 交易api
from .trade import (
    order_target_volume, order_target_value, order_target_percent,
    order_volume, order_percent, order_value, order_batch,
    order_cancel_all, order_cancel, order_close_all,
    get_orders, get_unfinished_orders)

# 数据查询api
from .query import (
    history_n, history, get_fundamentals, get_dividend, get_continuous_contracts, get_next_trading_date,
    get_previous_trading_date, get_trading_dates, get_concept, get_industry, get_constituents, get_history_constituents,
    get_history_instruments, get_instrumentinfos, get_instruments, get_sector, get_fundamentals_n
)


__all__ = [
    'order_target_volume', 'order_target_value', 'order_target_percent',
    'order_volume', 'order_percent', 'order_value', 'order_batch',
    'order_cancel_all', 'order_cancel', 'order_close_all',
    'get_orders', 'get_unfinished_orders',

    'set_token', 'get_version', 'subscribe', 'unsubscribe',
    'current', 'get_strerror', 'schedule', 'run',
    'set_parameter', 'add_parameter', 'log', 'stop',

    'history_n', 'history', 'get_fundamentals', 'get_dividend',
    'get_continuous_contracts', 'get_next_trading_date',
    'get_previous_trading_date', 'get_trading_dates', 'get_concept',
    'get_industry', 'get_constituents', 'get_history_constituents',
    'get_history_instruments', 'get_instrumentinfos', 'get_fundamentals_n',
    'get_instruments', 'get_sector', 'set_serv_addr',

    'ExecType_Unknown',
    'ExecType_New',
    'ExecType_DoneForDay',
    'ExecType_Canceled',
    'ExecType_PendingCancel',
    'ExecType_Stopped',
    'ExecType_Rejected',
    'ExecType_Suspended',
    'ExecType_PendingNew',
    'ExecType_Calculated',
    'ExecType_Expired',
    'ExecType_Restated',
    'ExecType_PendingReplace',
    'ExecType_Trade',
    'ExecType_TradeCorrect',
    'ExecType_TradeCancel',
    'ExecType_OrderStatus',
    'ExecType_CancelRejected',
    'OrderStatus_Unknown',
    'OrderStatus_New',
    'OrderStatus_PartiallyFilled',
    'OrderStatus_Filled',
    'OrderStatus_DoneForDay',
    'OrderStatus_Canceled',
    'OrderStatus_PendingCancel',
    'OrderStatus_Stopped',
    'OrderStatus_Rejected',
    'OrderStatus_Suspended',
    'OrderStatus_PendingNew',
    'OrderStatus_Calculated',
    'OrderStatus_Expired',
    'OrderStatus_AcceptedForBidding',
    'OrderStatus_PendingReplace',
    'OrderRejectReason_Unknown',
    'OrderRejectReason_RiskRuleCheckFailed',
    'OrderRejectReason_NoEnoughCash',
    'OrderRejectReason_NoEnoughPosition',
    'OrderRejectReason_IllegalAccountId',
    'OrderRejectReason_IllegalStrategyId',
    'OrderRejectReason_IllegalSymbol',
    'OrderRejectReason_IllegalVolume',
    'OrderRejectReason_IllegalPrice',
    'OrderRejectReason_AccountDisabled',
    'OrderRejectReason_AccountDisconnected',
    'OrderRejectReason_AccountLoggedout',
    'OrderRejectReason_NotInTradingSession',
    'OrderRejectReason_OrderTypeNotSupported',
    'OrderRejectReason_Throttle',
    'CancelOrderRejectReason_OrderFinalized',
    'CancelOrderRejectReason_UnknownOrder',
    'CancelOrderRejectReason_BrokerOption',
    'CancelOrderRejectReason_AlreadyInPendingCancel',
    'OrderSide_Unknown',
    'OrderSide_Buy',
    'OrderSide_Sell',
    'OrderType_Unknown',
    'OrderType_Limit',
    'OrderType_Market',
    'OrderType_Stop',
    'OrderDuration_Unknown',
    'OrderDuration_FAK',
    'OrderDuration_FOK',
    'OrderDuration_GFD',
    'OrderDuration_GFS',
    'OrderDuration_GTD',
    'OrderDuration_GTC',
    'OrderDuration_GFA',
    'OrderQualifier_Unknown',
    'OrderQualifier_BOC',
    'OrderQualifier_BOP',
    'OrderQualifier_B5TC',
    'OrderQualifier_B5TL',
    'OrderStyle_Unknown',
    'OrderStyle_Volume',
    'OrderStyle_Value',
    'OrderStyle_Percent',
    'OrderStyle_TargetVolume',
    'OrderStyle_TargetValue',
    'OrderStyle_TargetPercent',
    'PositionSide_Unknown',
    'PositionSide_Long',
    'PositionSide_Short',
    'PositionEffect_Unknown',
    'PositionEffect_Open',
    'PositionEffect_Close',
    'PositionEffect_CloseToday',
    'PositionEffect_CloseYesterday',
    'CashPositionChangeReason_Unknown',
    'CashPositionChangeReason_Trade',
    'CashPositionChangeReason_Inout',
    'MODE_LIVE',
    'MODE_BACKTEST',
    'ADJUST_NONE',
    'ADJUST_PREV',
    'ADJUST_POST',
    'SEC_TYPE_STOCK',
    'SEC_TYPE_FUND',
    'SEC_TYPE_INDEX',
    'SEC_TYPE_FUTURE',
    'SEC_TYPE_OPTION',
    'SEC_TYPE_CONFUTURE',

]

__all__ = [str(item) for item in __all__]
py_gmi_set_version(__version__.__version__, 'python')
