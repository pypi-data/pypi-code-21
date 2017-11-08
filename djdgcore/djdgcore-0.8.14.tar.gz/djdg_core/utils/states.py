#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/9/20
 """
from __future__ import unicode_literals, absolute_import
from django.utils import six
from djdg_core.exceptions import StanderResponseError
from djdg_core.exceptions import state_error


class StateMetaclass(type):
    """
    状态元类
    """
    @classmethod
    def get_state_machine(mcs, bases, attrs):
        machine_class = attrs.get('machine_class')
        if not machine_class:
            for base in bases:
                machine_class = getattr(base, 'machine_class', None)
                if machine_class:
                    break
        return machine_class

    def __new__(mcs, name, bases, attrs):
        machine_class = mcs.get_state_machine(bases, attrs)
        cls = super(StateMetaclass, mcs).__new__(mcs, name, bases, attrs)
        if machine_class:
            machine_class.register(cls)
        return cls


@six.add_metaclass(StateMetaclass)
class State(object):
    """
    状态
    """
    value = None
    max_value = None
    machine_class = None

    def __init__(self, context):
        self.context = context

    def __cmp__(self, other):
        return cmp(self.value, other)

    def transition(self, state=None):
        if self.value >= self.max_value:
            raise StanderResponseError(state_error.status, '该状态不能往下迁移！')
        state_machine = self.context['state_machine']
        cur_val = state if state is not None else self.value + 1
        value = min(cur_val, self.max_value)
        next_status = state_machine.get_state(value)
        return next_status

    def is_next_state(self, state):
        next_state = self.transition()
        return next_state == state


class StateMachine(object):
    """
    状态机
    """
    _states = None
    current_state = None
    context = None

    def __init__(self, current_state, **kwargs):
        kwargs['state_machine'] = self
        self.context = kwargs
        if isinstance(current_state, State):
            current_state = current_state.value
        status_cls = self._states[current_state]
        self.current_state = status_cls(context=self.context)

    @classmethod
    def register(cls, state_cls):
        if state_cls.value is not None:
            cls._states[state_cls.value] = state_cls

    def set_state(self, state):
        next_state = self.current_state.transition(state)
        if next_state == state:
            self.current_state = next_state
            return True
        return False

    def get_state(self, state):
        return self._states[state](self.context)


def state_machine_class():
    return type(b'StateMachineTemporary', (StateMachine, ), {'_states': {}})


def state_class(base, **kwargs):
    return type(b'StateTemporary', (base, ), kwargs)
