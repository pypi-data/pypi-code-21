import asyncio
import threading

import janus

from async_task_processor.exceptions import ATPException
from async_task_processor.primitives import BaseTask


class BaseProcessor:
    tasks = []
    _loop = None
    _atp = None
    _task_cls = None
    _main_thread_queue = None

    def __init__(self, atp, task_cls):
        """

        :type atp: async_task_processor.ATP
        :param task_cls: implementation class.
        """
        self._loop = atp.loop
        self._atp = atp
        self._task_cls = task_cls
        self._main_thread_queue = janus.Queue()
        self._loop.create_task(self.__main_thread_runtime_listener())

    async def __main_thread_runtime_listener(self):
        while True:
            command, data = await self._main_thread_queue.async_q.get()
            if command == 'start':
                tasks = self.__add_workers(data)
                self._loop.create_task(asyncio.gather(*[task.coroutine_future for task in tasks]))
            elif command == 'stop':
                self.stop(**data)

    def add_task(self, **kwargs):
        """You must override this method in processor. See task_processor.processors.TarantoolProcessor for example

        :param kwargs:
        * *task_workers* (``list of instances of BaseTask``) -- You must make tasks in custom processor method,
          then call super
         """
        if 'task_workers' not in kwargs or not isinstance(kwargs['task_workers'][0], BaseTask):
            raise ATPException(
                "you must make tasks in your processor implementation first. 'task_workers' must be in kwargs dict")
        self.__add_workers(kwargs['task_workers'])

    def __add_workers(self, task_workers):
        if not self.is_main_tread():
            self._main_thread_queue.sync_q.put(('start', task_workers))
        else:
            task_workers = [self.__make_future(task=t) for t in task_workers]
            self.tasks.extend(task_workers)
            return task_workers

    def __make_future(self, task):
        """

        :param task:
        :return:
        """
        task.set_future(asyncio.ensure_future(self._task_cls.async_task_coro(task=task)))
        task.set_app(self._atp)
        task.set_processor(self)
        return task

    def stop(self, task_name=None, task_id=None, workers_count=1, leave_last=False):
        """Stop task workers. You can stop task or tasks by  name or id.

        :param task_name: task name
        :type task_name: str
        :param task_id: task id
        :type task_name: str
        :param workers_count: number of workers to stop
        :type workers_count: int
        :param leave_last: if true always leave one worker. It works if only task_name argument is present
        :type leave_last: bool
        :return:
        """
        if not self.is_main_tread():
            self._main_thread_queue.sync_q.put(('stop',
                                                dict(task_name=task_name, task_id=task_id, workers_count=workers_count,
                                                     leave_last=leave_last)))
            return
        if task_id:
            tasks4stop = self.filter_by_id(task_id)
        else:
            tasks4stop = self.filter_by_name(task_name)
            tasks4stop = tasks4stop[:workers_count]
            if leave_last and len(tasks4stop) == workers_count:
                tasks4stop = tasks4stop[:-1]
        if tasks4stop:
            [task.remove() for task in tasks4stop]
            [task.shutdown() for task in tasks4stop]
        else:
            self._atp.logger.warning('can\'t find task to stop')
        return tasks4stop

    def filter_by_name(self, task_name):
        return list(filter(lambda x: x.name == task_name, self.tasks))

    def filter_by_id(self, task_id):
        return list(filter(lambda x: str(x.id) == task_id, self.tasks))

    @staticmethod
    def is_main_tread():
        return threading.get_ident() == threading.main_thread().ident
