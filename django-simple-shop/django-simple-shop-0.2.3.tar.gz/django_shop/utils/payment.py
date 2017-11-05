# coding=utf8
from __future__ import unicode_literals, absolute_import

from .hooks import HooksManager

_payment_manager = None


def create_payment(hook_name, order):
    if _payment_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _payment_manager.create_object(hook_name, order)


def get_payment(hook_name, order):
    if _payment_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _payment_manager.get_object(hook_name, order)


def get_model_choices():
    if _payment_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _payment_manager.get_model_choices()


def get_description(hook_name):
    if _payment_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _payment_manager.get_description(hook_name)


def initiate_payment_manager(hooks):
    global _payment_manager
    _payment_manager = HooksManager(hooks, allow_empty=True)
