# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

SUB_ID = 'SUB_ID:{}:{}:{}'  # 订阅股票唯一id  由三部分组成  symbol frequency count
SUB_TAG = 'SUB_TAG:{}:{}'  # 取消订阅股票标签 由两部分组成  symbol frequency

DATA_TYPE_TICK = 'tick'
DATA_TYPE_BAR = 'bar'

"""
c-sdk回调的类型
"""
CALLBACK_TYPE_TICK = 'data.api.Tick'
CALLBACK_TYPE_BAR = 'data.api.Bar'
CALLBACK_TYPE_SCHEDULE = 'schedule'
CALLBACK_TYPE_EXECRPT = 'core.api.ExecRpt'
CALLBACK_TYPE_ORDER = 'core.api.Order'
CALLBACK_TYPE_INDICATOR = 'core.api.Indicator'
CALLBACK_TYPE_CASH = 'core.api.Cash'
CALLBACK_TYPE_POSITION = 'core.api.Position'
CALLBACK_TYPE_PARAMETERS = 'runtime-config'
CALLBACK_TYPE_ERROR = 'error'
CALLBACK_TYPE_TIMER = 'timer'

SCHEDULE_INFO = 'date_rule={date_rule},time_rule={time_rule}'

HISTORY_ADDR = 'ds-history-rpc'
HISTORY_REST_ADDR = 'ds-history-rpcgw'
FUNDAMENTAL_ADDR = 'ds-fundamental-rpc'

CSDK_OPERATE_SUCCESS = 0  # c-sdk 操作成功

ERROR_FORMAT = 'error code={}, error info={}'