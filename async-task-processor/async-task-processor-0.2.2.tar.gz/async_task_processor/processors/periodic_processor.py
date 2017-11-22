import asyncio
import sys
import traceback

from async_task_processor.exceptions import RetryException
from async_task_processor.processors.simple_processor import SimpleProcessor


class PeriodicProcessor(SimpleProcessor):
    """Processor for simple periodic tasks with interval

    """

    async def async_task_coro(self, task):
        """

        :type task: async_task_processor.primitives.TarantoolTask
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
            await asyncio.sleep(task.timeout)
        task.shutdown()
