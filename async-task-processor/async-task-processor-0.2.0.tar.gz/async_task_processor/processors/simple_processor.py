import asyncio
import sys
import traceback

from async_task_processor.exceptions import RetryException
from async_task_processor.primitives import Task
from async_task_processor.processors.base_processor import BaseProcessor


class SimpleProcessor(BaseProcessor):
    """Processor for simple tasks

    """

    def __init__(self, atp):
        """

        :type atp: async_task_processor.atp.ATP
        """
        super().__init__(atp=atp, task_cls=self)

    def add_task(self, foo, args=None, bind=None, max_workers=1, timeout=0, max_retries=0, retry_countdown=0,
                 name=None):
        """Add task to processor

        :param foo: function that will work in parallel
        :param args: function arguments
        :type args: list
        :param bind: If True, then task will be passed to function by the first argument. There is a loop and more
         specific data will be there
        :type bind: bool
        :param max_workers: Number of async copies
        :type max_workers: int
        :type timeout: int or float (seconds)
        :param max_retries: Maximum of retries, when the exception is caught. You mast call self.retry.
        :type max_retries: int
        :param retry_countdown: Timeout between retries
        :type retry_countdown: int or float (seconds)
        :param name: name of task, if empty foo.__name__ will be used
        :return:
        """
        task_workers = [Task(loop=self._loop, foo=foo, args=args, bind=bind, timeout=timeout, max_retries=max_retries,
                             retry_countdown=retry_countdown, name=name) for _ in range(max_workers)]
        super().add_task(task_workers=task_workers)

    async def async_task_coro(self, task):
        """

        :type task: async_task_processor.primitives.Task
        :return:
        """
        while True:
            # check task was removed
            if task not in task.app.tasks:
                break
            arguments = [] if not task.bind else [task]
            if task.args:
                arguments.extend(task.args)
            try:
                await asyncio.ensure_future(task.loop.run_in_executor(task.executor, task.foo, *arguments))
            except asyncio.CancelledError:
                pass
            except RetryException as exc:
                await asyncio.sleep(task.retry_countdown)
                task.app.logger.warning(exc)
                continue
            except Exception:
                task.remove()
                task.app.logger.error(
                    'worker down with exception: {exception}, traceback:\n {traceback}'.format(
                        exception=repr(sys.exc_info()[0]), traceback=traceback.format_exc()))
                break
            task.retries = 0
            task.exception = None
            break
        task.shutdown()
