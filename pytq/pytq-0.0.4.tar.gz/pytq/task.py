#!/usr/bin/env python
# -*- coding: utf-8 -*-

import attr

try:
    from .pkg.attrs_mate import AttrsClass
except:
    from pytq.pkg.attrs_mate import AttrsClass


def none_or_is_callable(instance, attribute, value):
    """
    Can be None or callable.
    """
    if value is not None and not callable(value):
        raise TypeError(
            'callback must be a callable, got %s' % type(value).__name__)


@attr.s
class Task(AttrsClass):
    id = attr.ib()
    input_data = attr.ib()
    nth_counter = attr.ib(default=None)  # integer
    left_counter = attr.ib(default=None)  # integer
    output_data = attr.ib(default=None)
    pre_process = attr.ib(  # a callable function
        default=None,
        validator=none_or_is_callable,
    )
    post_process = attr.ib(  # a callable function
        default=None,
        validator=none_or_is_callable,
    )

    def _pre_process(self):
        self.pre_process(self)

    def _post_process(self):
        self.post_process(self)

    def progress_msg(self):
        """
        Generate progress message.
        """
        if self.nth_counter is None:
            msg = "Process: InputData(%r) ..." % self.input_data
            return msg

        if self.left_counter is None:
            msg = "Process %sth: InputData(%r) ..." % (
                self.nth_counter, self.input_data,
            )
        else:
            msg = "Process %sth: InputData(%r); %s left ..." % (
                self.nth_counter, self.input_data, self.left_counter,
            )
        return msg
