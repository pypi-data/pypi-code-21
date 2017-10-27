import time

from simpleflow import (
    activity,
)


@activity.with_attributes(task_list='quickstart', version='example')
def increment(x):
    return x + 1


@activity.with_attributes(task_list='quickstart', version='example')
def double(x):
    return x * 2


# simpleflow activities can be classes ; in that case the class is instantiated
# with the params passed via submit, then the `execute()` method is called and
# the result is returned.
@activity.with_attributes(task_list='quickstart', version='example')
class Delay(object):
    def __init__(self, t, x):
        self.t = t
        self.x = x

    def execute(self):
        time.sleep(self.t)
        return self.x
