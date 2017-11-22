import asyncio
import logging
import signal
import sys

from async_task_processor.exceptions import ATPException


class ATP:
    tasks = []
    logger = None
    loop = None

    def __init__(self, loop=None, asyncio_debug=False, logger=None):
        """

        :type loop: uvloop.Loop
        :type asyncio_debug: bool
        :type logger: logging.Logger
        """
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = loop or asyncio.get_event_loop()
        self.loop.set_debug(asyncio_debug)
        self.logger = logger or logging.getLogger("async_task_processor")

    def _signal_handler(self):
        """Signal handler

        :return:
        """
        self.logger.info("canceling all pending tasks ...")
        [task.cancel() for task in self.tasks]
        self.logger.info("all tasks canceled, exit...")
        sys.exit(0)

    def add_tasks(self, *tasks):
        """Add tasks

        :param tasks:
        :return:
        """
        self.tasks.extend(tasks)

    def start(self):
        """Start async task workers

        :return:
        """
        if not self.tasks:
            raise ATPException(
                'you must add some task`s in TaskRunner instance first, use add_tasks method')
        for sig in ('SIGINT', 'SIGTERM'):
            self.loop.add_signal_handler(getattr(signal, sig), self._signal_handler)
        try:
            self.loop.run_until_complete(asyncio.gather(*[task.coroutine_future for task in self.tasks]))
        except asyncio.CancelledError:
            pass

    def filter(self, task_name):
        return list(filter(lambda x: x[1].name == task_name, enumerate(self.tasks)))
