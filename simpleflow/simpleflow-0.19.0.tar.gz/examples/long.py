from __future__ import print_function
import time

from simpleflow import (
    activity,
    Workflow,
    futures,
)


@activity.with_attributes(task_list='quickstart', version='example',
                          start_to_close_timeout=90, heartbeat_timeout=10,
                          raises_on_failure=True)
def sleep150():
    print("will sleep")
    time.sleep(15)
    print("good sleep")

class LongWorkflow(Workflow):
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self):
        x = self.submit(sleep150)
        futures.wait(x)
