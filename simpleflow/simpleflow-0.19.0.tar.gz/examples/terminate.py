from __future__ import print_function
import time

from simpleflow import (
    activity,
    Workflow,
    futures,
)


@activity.with_attributes(task_list='quickstart', version='example')
def sleep150():
    print("will sleep")
    time.sleep(150)
    print("good sleep")

class WillIKillMyself(Workflow):
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self):
        x = self.submit(sleep150)
        futures.wait(x)
