#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/1
 """
from __future__ import unicode_literals, absolute_import
from django.db import models


class PayResult(models.Model):
    """
    支付结果信息
    """
    notify_time = models.DateTimeField('通知时间', auto_now_add=True)
    notify_type = models.CharField(max_length=128, verbose_name='通知类型', null=True)
    notify_id = models.IntegerField(verbose_name='通知id')
    order_id = models.IntegerField('订单id')
    total_fee = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='订单总额', default=0)
    cash_fee = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='实际支付金额', default=0)
    coupon_fee = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='代金券或者优惠金额', default=0)
    coupon_count = models.IntegerField('代金券或立减优惠使用数量', default=0)
    pay_time = models.DateTimeField('支付时间', auto_now_add=True)
    pay_way = models.IntegerField('支付类型', null=True)
    app_id = models.CharField(max_length=64, verbose_name='app id', null=True)
    pay_type = models.CharField(max_length=64, verbose_name='支付类型', null=True, blank=True)
    create_time = models.DateTimeField('记录创建时间', auto_now_add=True)


class AllocateRecord(models.Model):
    """
    会员宝分账记录
    """
    request_no = models.CharField(max_length=128, verbose_name='请求id')
    notify_id = models.IntegerField(verbose_name='通知id')
    app_id = models.CharField(max_length=128, verbose_name='appid 对应 merchantId')
    operator_id = models.PositiveSmallIntegerField('操作id')
    user_id = models.IntegerField('用户id，对应userIn')
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='金额')
    desc = models.TextField('描述')
    create_time = models.DateTimeField('记录创建时间', auto_now_add=True)


class RefundRecord(models.Model):
    """
    会员宝退款记录
    """
    notify_id = models.IntegerField(verbose_name='通知id')
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='计划退回金额')
    confirm_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='实际退回金额')
    order_id = models.IntegerField('订单id')
    refund_id = models.CharField(max_length=64,verbose_name='退款id，由会员宝返回')
    user_id = models.IntegerField('退款用户id，即common api的用户id')
    create_time = models.DateTimeField('记录创建时间', auto_now_add=True)