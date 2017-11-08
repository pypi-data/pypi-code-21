#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/3
 """
from __future__ import unicode_literals, absolute_import
from django.db.transaction import atomic
from djdg_core.memberbao.public import memberbao_client
from djdg_core.memberbao.models import RefundRecord
from djdg_core.memberbao.models import PayResult
from djdg_core.exceptions import StanderResponseError
from djdg_core.memberbao import errors


def allocate(notify_id, app_id, operator_id, allocate_rules, request_no):
    """
    会员宝分账接口
    :param notify_id:
    :param app_id:
    :param operator_id:
    :param allocate_rules:
    :param request_no:
    :return:
    """
    res = memberbao_client.get_resource('order')
    data = {
        'requestNo': request_no,
        'notifyId': notify_id,
        'merchantId': app_id,
        'operatorId': operator_id,
        'allocateRules': allocate_rules
    }
    ret = res.post.allocate(data=data)
    return ret.data


def refund(amount, order_id, user_id):
    """
    会员宝退款
    :param amount:
    :param order_id:
    :param user_id:
    :return:
    """
    refund_record = None
    ret = None
    with atomic():
        pay_result = PayResult.objects.filter(order_id=order_id).first()
        if not pay_result:
            raise StanderResponseError(
                errors.PAY_RESULT_NOT_FOUND,
                '没有找到订单[{}]的支付结果记录！'.format(order_id)
            )
        res = memberbao_client.get_resource('refund')
        data = {
            'notifyId': pay_result.notify_id,
             'refundAmount': amount
        }
        ret = res.post(data=data)
        refund_record = RefundRecord.objects.create(
            notify_id=pay_result.notify_id,
            amount=amount,
            order_id=order_id,
            refund_id=ret.data['refundId'],
            user_id=user_id,
            confirm_amount=ret.data['refundAmount']
        )
    dif = abs(refund_record.amount - refund_record.confirm_amount)
    if dif > 0.001:
        raise StanderResponseError(
            errors.REFUND_AMOUNT_NOT_RIGHT,
            '会员宝退款金额[{am}/{cam}]不一致！'.format(
                am=refund_record.amount,
                cam=refund_record.confirm_amount

            )
        )
    return ret.data
