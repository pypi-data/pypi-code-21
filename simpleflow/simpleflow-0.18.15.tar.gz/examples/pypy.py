#!/usr/bin/env python

from __future__ import print_function

from examples.version import fn
from simpleflow import activity, Workflow


def as_activity(func):
    """
    This decorator provides default values for the activities's attributes.

    We should rather decorate each activity individually to set the right
    values, especially for timeouts.
    :param func:
    :rtype: simpleflow.activity.Activity
    """
    return activity.with_attributes(
        version='example',
        task_list='quickstart',
        raises_on_failure=True,
    )(func)


class AWorkflow(Workflow):
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self):
        a_fn = as_activity(fn)
        print(self.submit(a_fn).result)
