from __future__ import print_function
import time

from simpleflow import (
    activity,
    Workflow,
    futures,
)
from simpleflow.exceptions import ExecutionBlocked


@activity.with_attributes(task_list='quickstart', version='example',
                          start_to_close_timeout=60, heartbeat_timeout=15,
                          raises_on_failure=True)
def func():
    print("\033[93mStarted executing func()\033[0m")
    time.sleep(5)
    print("\033[93mFinished executing func()\033[0m")

class AccessHistoryWorkflow(Workflow):
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self):
        x = self.submit(func)
        if 'activity-examples.access_history.func-1' in self._executor._history.activities:
            print("\033[93mfunc() has been executed!\033[0m")
        else:
            print("\033[93mfunc() not executed yet, blocking\033[0m")
            raise ExecutionBlocked()
