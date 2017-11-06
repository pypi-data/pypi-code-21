# coding=utf-8
"""
回调任务分发
"""
from __future__ import unicode_literals, print_function, absolute_import
import datetime

import sys

from gm.constant import CALLBACK_TYPE_TICK, CALLBACK_TYPE_BAR, \
    CALLBACK_TYPE_SCHEDULE, CALLBACK_TYPE_EXECRPT, \
    CALLBACK_TYPE_ORDER, CALLBACK_TYPE_INDICATOR, CALLBACK_TYPE_CASH, \
    CALLBACK_TYPE_POSITION, CALLBACK_TYPE_PARAMETERS, CALLBACK_TYPE_ERROR, \
    CALLBACK_TYPE_TIMER, CALLBACK_TYPE_BACKTEST_FINISH, CALLBACK_TYPE_STOP
from gm.enum import MODE_LIVE, MODE_BACKTEST
from gm.model.storage import context
from gm.model.storage_data import SubBarData
from gm.pb.account_pb2 import ExecRpt, Order, Cash, Position
from gm.pb.performance_pb2 import Indicator
from gm.pb.rtconf_pb2 import Parameters
from gm.pb_to_dict import protobuf_to_dict
from gm.utils import ObjectLikeDict

sub_bar_data = SubBarData()


def tick_callback(data):
    if not hasattr(context.inside_file_module, 'on_tick'):
        return
    tick = _pack_tick_info(data)
    context.inside_file_module.on_tick(context, tick)


def bar_callback(data):
    if not hasattr(context.inside_file_module, 'on_bar'):
        return
    bar = _pack_bar_info(data)
    # 注意:塞入queue的应该是一个字典对象
    sub_bar_data.set_data(bar)
    [task.set_wait_perform_eob(bar) for task in context.inside_bar_tasks ]
    # 回测时, 在这里出发任务检查
    _trigger_task()


def _trigger_task():
    if context.mode == MODE_LIVE:
        for task in context.inside_bar_tasks:
            # 任务标记
            task.state_analysis_mode_live()
            #  执行被触发的任务
            if task.waiting:
                context.inside_file_module.on_bar(context, task.get_perform_bars())
                task.reset()

    if context.mode == MODE_BACKTEST:
        for task in context.inside_bar_tasks:
            task.state_analysis_mode_backtest()
            if task.waiting:
                context.inside_file_module.on_bar(context, task.get_perform_bars())
                task.reset()


def schedule_callback(data):
    # python 3 传过来的是bytes 类型， 转成str
    if isinstance(data, bytes):
        data = bytes.decode(data)

    schedule_func = context.inside_schedules.get(data)
    if not schedule_func:
        return

    schedule_func(context)


def excerpt_callback(data):
    if not hasattr(context.inside_file_module, 'on_execution_report'):
        return

    excerpt = ExecRpt()
    excerpt.ParseFromString(data)
    excerpt = protobuf_to_dict(excerpt)
    context.inside_file_module.on_execution_report(context, excerpt)


def order_callback(data):
    if not hasattr(context.inside_file_module, 'on_order_status'):
        return

    order = Order()
    order.ParseFromString(data)
    order = protobuf_to_dict(order)
    context.inside_file_module.on_order_status(context, order)


def indicator_callback(data):
    if not hasattr(context.inside_file_module, 'on_backtest_finished'):
        return

    indicator = Indicator()
    indicator.ParseFromString(data)
    indicator = protobuf_to_dict(indicator)
    context.inside_file_module.on_backtest_finished(context, indicator)


def cash_callback(data):
    cash = Cash()
    cash.ParseFromString(data)
    cash = protobuf_to_dict(cash)
    account_id = cash['account_id']
    accounts = context.accounts
    accounts[account_id].cash = cash


def position_callback(data):
    position = Position()
    position.ParseFromString(data)
    position = protobuf_to_dict(position, including_default_value_fields=True)
    symbol = position['symbol']
    side = position['side']
    account_id = position['account_id']
    accounts = context.accounts
    position_key = '{}.{}'.format(symbol, side)
    accounts[account_id].inside_positions[position_key] = position

    if not position['amount'] and not position['volume']:
        if accounts[account_id].inside_positions.get(position_key):
            return accounts[account_id].inside_positions.pop(position_key)


def parameters_callback(data):
    parameters = Parameters()
    parameters.ParseFromString(data)
    parameters = [protobuf_to_dict(p) for p in parameters.parameters]
    if hasattr(context.inside_file_module, 'on_parameter'):
        context.inside_file_module.on_parameter(context, parameters[0])


def err_callback(data):
    # python 3 传过来的是bytes 类型， 转成str
    if not hasattr(context.inside_file_module, 'on_error'):
        return

    if isinstance(data, bytes):
        data = bytes.decode(data)

    code, info = data.split('|')
    context.inside_file_module.on_error(context, code, info)


def timer_callback(data):
    _trigger_task()


def backtest_finish_callback(data):
    #  执行最后没有被触发的任务
    for task in context.inside_bar_tasks:
        if not task.waiting and task.get_perform_bars():
            context.inside_file_module.on_bar(context, task.get_perform_bars())


def stop_callback(data):
    from gm.api import stop
    stop()


def callback_controller(msg_type, data):
    """
    回调任务控制器
    """
    # python 3 传过来的是bytes 类型， 转成str
    if isinstance(msg_type, bytes):
        msg_type = bytes.decode(msg_type)

    if msg_type == CALLBACK_TYPE_TICK:
        return tick_callback(data)

    if msg_type == CALLBACK_TYPE_BAR:
        if context.mode == MODE_BACKTEST:
            _trigger_task()

        return bar_callback(data)

    if msg_type == CALLBACK_TYPE_SCHEDULE:
        if context.mode == MODE_BACKTEST:
            _trigger_task()

        return schedule_callback(data)

    if msg_type == CALLBACK_TYPE_ERROR:
        return err_callback(data)

    if msg_type == CALLBACK_TYPE_TIMER:
        return timer_callback(data)

    if msg_type == CALLBACK_TYPE_EXECRPT:
        return excerpt_callback(data)

    if msg_type == CALLBACK_TYPE_ORDER:
        return order_callback(data)

    if msg_type == CALLBACK_TYPE_INDICATOR:
        return indicator_callback(data)

    if msg_type == CALLBACK_TYPE_CASH:
        return cash_callback(data)
    
    if msg_type == CALLBACK_TYPE_POSITION:
        return position_callback(data)
    
    if msg_type == CALLBACK_TYPE_PARAMETERS:
        return parameters_callback(data)

    if msg_type == CALLBACK_TYPE_BACKTEST_FINISH:
        return backtest_finish_callback(data)

    if msg_type == CALLBACK_TYPE_STOP:
        return stop_callback(data)


def _pack_tick_info(data):
    quotes = []
    for x in range(1, 6):
        quote = {
            'bid_p': data['bid_p{}'.format(x)],
            'bid_v': data['bid_v{}'.format(x)],
            'ask_p': data['ask_p{}'.format(x)],
            'ask_v': data['ask_v{}'.format(x)],
        }

        if quote['bid_p'] and quote['ask_p']:
            quotes.append(quote)

    data['quotes'] = quotes
    data['created_at'] = datetime.datetime.fromtimestamp(data['created_at'])

    # 防止打印的时候带上这些不应该显示的信息
    remove_keys = ['bid_p1', 'bid_p2', 'bid_p3', 'bid_p4', 'bid_p5',
                   'bid_v1', 'bid_v2', 'bid_v3', 'bid_v4', 'bid_v5',
                   'ask_v1', 'ask_v2', 'ask_v3', 'ask_v4', 'ask_v5',
                   'ask_p1', 'ask_p2', 'ask_p3', 'ask_p4', 'ask_p5']

    for remove_key in remove_keys:
        data.pop(remove_key)

    return ObjectLikeDict(data)


def _pack_bar_info(data):
    data['eob'] = datetime.datetime.fromtimestamp(data['eob'])
    data['bob'] = datetime.datetime.fromtimestamp(data['bob'])

    # todo 暂时自行适配 明天查一下cython能不能定义输入输出
    if sys.version_info >= (3, 0):
        for key in data:
            if isinstance(data[key], bytes):
                data[key] = data[key].decode()

    return data