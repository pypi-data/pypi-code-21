# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

from gm.constant import CSDK_OPERATE_SUCCESS
from gm.csdk.c_sdk import py_gmi_place_order, py_gmi_get_unfinished_orders, \
    py_gmi_get_orders, py_gmi_cancel_all_orders, \
    py_gmi_close_all_positions, py_gmi_cancel_order
from gm.enum import OrderQualifier_Unknown, OrderDuration_Unknown, MODE_BACKTEST
from gm.model.storage import Context
from gm.pb.account_pb2 import Order, Orders, OrderStyle_Volume, \
    OrderStyle_Value, OrderStyle_Percent, \
    OrderStyle_TargetVolume, OrderStyle_TargetValue, OrderStyle_TargetPercent
from gm.pb.trade_pb2 import GetUnfinishedOrdersReq, GetOrdersReq, \
    CancelAllOrdersReq, CloseAllPositionsReq
from gm.pb_to_dict import protobuf_to_dict
from gm.utils import load_to_list, datetime2timestamp

context = Context()


def _place_order(**kwargs):
    order = Order()

    for key in kwargs:
        setattr(order, key, kwargs[key])
        if context.mode == MODE_BACKTEST:
            order.created_at.seconds = datetime2timestamp(context.now,
                                                          convert_to_utc=False)

    orders = Orders()
    orders.data.extend([order])

    req = orders.SerializeToString()
    status, result = py_gmi_place_order(req)
    if not status == CSDK_OPERATE_SUCCESS:
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    return [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]


def order_volume(symbol, volume, side, order_type,
                 position_effect, price=0, order_duration=OrderDuration_Unknown, order_qualifier=OrderQualifier_Unknown,account=''):
    """
    按指定量委托
    """
    order_style = OrderStyle_Volume
    account_id = get_account_id(account)

    return _place_order(symbol=symbol, volume=volume, price=price,
                        side=side, order_type=order_type, position_effect=position_effect,
                        order_style=order_style,
                        order_qualifier=order_qualifier,
                        order_duration=order_duration,
                        account_id=account_id)


def order_value(symbol, value,  side,  order_type,
                position_effect, price=0, order_duration=OrderDuration_Unknown, order_qualifier=OrderQualifier_Unknown,account=''):
    """
    按指定价值委托
    """
    order_style = OrderStyle_Value
    account_id = get_account_id(account)

    return _place_order(symbol=symbol, value=value, price=price,
                        side=side, order_type=order_type, position_effect=position_effect,
                        order_style=order_style,
                        order_qualifier=order_qualifier,
                        order_duration=order_duration,
                        account_id=account_id)


def order_percent(symbol, percent, side, order_type,
                  position_effect, price=0, order_duration=OrderDuration_Unknown, order_qualifier=OrderQualifier_Unknown, account=''):
    """
    按指定比例委托
    """
    order_style = OrderStyle_Percent
    account_id = get_account_id(account)

    return _place_order(symbol=symbol, percent=percent, price=price,
                        side=side, order_type=order_type,
                        position_effect=position_effect,
                        order_qualifier=order_qualifier,
                        order_duration=order_duration,
                        order_style=order_style, account_id=account_id)


def order_target_volume(symbol, volume, position_side,
                        order_type, price=0, order_duration=OrderDuration_Unknown,
                        order_qualifier=OrderQualifier_Unknown, account=''):
    """
    调仓到目标持仓量
    """
    order_style = OrderStyle_TargetVolume
    account_id = get_account_id(account)

    return _place_order(symbol=symbol, target_volume=volume, price=price,
                        position_side=position_side, order_type=order_type,
                        order_qualifier=order_qualifier,
                        order_duration=order_duration,
                        order_style=order_style, account_id=account_id)


def order_target_value(symbol, value, position_side,
                       order_type, price=0,
                       order_duration=OrderDuration_Unknown, order_qualifier=OrderQualifier_Unknown,
                       account=''):
    """
    调仓到目标持仓额
    """
    order_style = OrderStyle_TargetValue
    account_id = get_account_id(account)

    return _place_order(symbol=symbol, target_value=value, price=price,
                        position_side=position_side, order_type=order_type,
                        order_qualifier=order_qualifier,
                        order_duration=order_duration,
                        order_style=order_style, account_id=account_id)


def order_target_percent(symbol, percent, position_side,
                         order_type, price=0,
                         order_duration=OrderDuration_Unknown,
                         order_qualifier=OrderQualifier_Unknown,
                         account=''):
    """
    调仓到目标持仓比例
    """
    order_style = OrderStyle_TargetPercent
    account_id = get_account_id(account)

    return _place_order(symbol=symbol, target_percent=percent, price=price,
                        position_side=position_side, order_type=order_type,
                        order_qualifier=order_qualifier,
                        order_duration=order_duration,
                        order_style=order_style, account_id=account_id)


def get_unfinished_orders():
    """
    查询所有未结委托
    """
    req = GetUnfinishedOrdersReq()
    req = req.SerializeToString()
    status, result = py_gmi_get_unfinished_orders(req)
    if not status == CSDK_OPERATE_SUCCESS:
        return []

    res = Orders()
    res.ParseFromString(result)

    return [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]


def get_orders():
    """
    查询日内全部委托
    """
    req = GetOrdersReq()
    req = req.SerializeToString()
    status, result = py_gmi_get_orders(req)
    if not status == CSDK_OPERATE_SUCCESS:
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    return [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]


def order_cancel_all():
    """
    撤销所有委托
    """
    req = CancelAllOrdersReq()
    req = req.SerializeToString()
    py_gmi_cancel_all_orders(req)


def order_close_all():
    """
    平当前所有可平持仓
    """
    req = CloseAllPositionsReq()
    req = req.SerializeToString()
    status, result = py_gmi_close_all_positions(req)
    if not status == CSDK_OPERATE_SUCCESS:
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    return [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]


def order_cancel(wait_cancel_orders):
    """
    撤销委托
    """
    wait_cancel_orders = load_to_list(wait_cancel_orders)

    orders = Orders()
    cl_ord_ids = [order['cl_ord_id'] for order in wait_cancel_orders]

    for cl_ord_id in cl_ord_ids:
        order = orders.data.add()
        order.cl_ord_id = cl_ord_id
    req = orders.SerializeToString()
    py_gmi_cancel_order(req)


def order_batch(order_infos, combine=False, account=''):
    """
    批量委托接口
    """
    orders = Orders()
    for order_info in order_infos:
        order_info['account_id'] = get_account_id(account)
        order = orders.data.add()
        [setattr(order, k, order_info[k]) for k in order_info]
        if context.mode == MODE_BACKTEST:
            order.created_at.seconds = datetime2timestamp(context.now,
                                                          convert_to_utc=False)

    req = orders.SerializeToString()
    status, result = py_gmi_place_order(req)
    if not status == CSDK_OPERATE_SUCCESS:
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    return [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]


def get_account_id(name_or_id):
    for one in context.accounts.values():
        if one.match(name_or_id):
            return one.id

    # 都没有匹配上， 等着后端去拒绝
    return name_or_id
