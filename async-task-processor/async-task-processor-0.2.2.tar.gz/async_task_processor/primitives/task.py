from async_task_processor.primitives.base_task import BaseTask


class Task(BaseTask):
    def __init__(self, loop, foo, args, bind, timeout, max_retries, retry_countdown, name):
        super().__init__(loop, type(self).__name__, foo, args, bind, timeout, max_retries, retry_countdown, name)
