#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
import attr

try:
    from .pkg.attrs_mate import AttrsClass
except:  # pragma: no cover
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
    """
    Task is the core concept for task queue application.

    :param id: str or int, fingerprint of input_data.
    :param input_data: input data of the task.
    :param nth_counter: its the nth task in the entire queue.
    :param left_counter: there's nth task left for the entire batch job.
    :param output_data: after processing, the output data you got, could
        includes anything, such as, raw data, status, errors.
    :param pre_process: a callable function for single task, will be called
        before the process function been called.
    :param post_process: a callable function for single task, will be called
        after the process function been called.
    """
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

    def progress_msg(self):  # pragma: no cover
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
