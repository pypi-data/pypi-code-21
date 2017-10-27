# This example implements an inifinite loop so we can test activity workers things
# or things in console via boto.swf / whatever
import random
import time
from simpleflow import activity, Workflow


@activity.with_attributes(
    task_list="infinite",
    version="1.0",
    idempotent=True,
    retry=5
)
def print_params(*args, **kwargs):
    print("INFO: received args={} and kwargs={}".format(args, kwargs))
    time.sleep(1)
    if random.randint(1, 10) < 3:
        raise ValueError("foo")
    return args[0] + 1


class InfiniteWorkflow(Workflow):
    name = "infinite"
    version = "1.0"
    task_list = "infinite"

    def run(self):
        x = 0
        for i in xrange(0, 3000):
            result = self.submit(print_params, x).result
            if result:
                x = result

        print("final value: {}".format(x))
