import asyncio
import sys
import traceback

import asynctnt
import asynctnt_queue
from asynctnt.exceptions import TarantoolNotConnectedError
from tarantool import NetworkError

from async_task_processor.exceptions import RetryException
from async_task_processor.primitives import TarantoolTask
from async_task_processor.processors.base_processor import BaseProcessor


class TarantoolProcessor(BaseProcessor):
    """Processor for obtaining tasks from tarantool queue

    """
    _conn_max_retries = None
    _conn_retry_countdown = None
    _queue = None
    _connection = None

    def __init__(self, atp, host='localhost', port=8123, user=None,
                 password=None, encoding='utf-8', connection_max_retries=0, connection_retry_countdown=0):
        """

        :type atp: async_task_processor.atp.ATP
        :param host: tarantool host
        :param port: tarantool port
        :param user: tarantool user
        :param password: tarantool password
        :param encoding: tarantool data encoding
        :param connection_max_retries: maximum number of retries, when the connection is broken.
        :param connection_retry_countdown: timeout between connection retries
        """
        super().__init__(atp=atp, task_cls=self)
        self._conn_max_retries = connection_max_retries
        self._conn_retry_countdown = connection_retry_countdown
        self._loop.run_until_complete(asyncio.ensure_future(self._connect(host=host, port=port, user=user,
                                                                          password=password, encoding=encoding)))

    async def _connect(self, host, port, user, password, encoding):
        conn = asynctnt.Connection(host=host, port=port, username=user, password=password, encoding=encoding)
        await conn.connect()
        self._connection = conn
        self._queue = asynctnt_queue.Queue(conn)

    def add_task(self, queue, foo, args=None, bind=None, max_workers=1, timeout=0, max_retries=0, retry_countdown=0,
                 name=None):
        """Add task to processor

        :param queue: Tarantool queue name
        :type queue: str
        :param foo: function that will work in parallel
        :param args: Function arguments
        :type args: list
        :param bind: If True, then task will be passed to function by the first argument. There is a loop and more
         specific data will be there
        :type bind: bool
        :param max_workers: Number of async copies
        :type max_workers: int
        :type timeout: int or float (seconds)
        :param max_retries: Maximum number of retries, when exception is caught. You mast call self.retry.
        :type max_retries: int
        :param retry_countdown: Timeout between retries (seconds)
        :type retry_countdown: int or float
        :param name: name of task, if empty foo.__name__ will be used
        :return:
        """
        task_workers = [
            TarantoolTask(loop=self._loop, connection=self._connection, tube=self._queue.tube(queue), foo=foo,
                          args=args, bind=bind, timeout=timeout, max_retries=max_retries,
                          retry_countdown=retry_countdown, conn_max_retries=self._conn_max_retries,
                          conn_retry_countdown=self._conn_retry_countdown, name=name)
            for _ in range(max_workers)]
        super().add_task(task_workers=task_workers)

    @staticmethod
    async def async_task_coro(task):
        """

        :type task: TarantoolTask
        :return:
        """
        while True:
            # check task was removed
            if task not in task.app.tasks:
                break
            # check task on retry
            if not task.retries:
                try:
                    tube_task = await task.tube.take(5)
                    if tube_task:
                        task.set_tube(tube_task)
                    task.conn_retries = 0
                except (TarantoolNotConnectedError, NetworkError):
                    if task.conn_max_retries == task.conn_retries:
                        raise
                    await asyncio.sleep(task.conn_retry_countdown)
                    task.app.logger.warning(
                        'Tarantool connection problems, trying to reconnect #%d' % (task.conn_retries + 1))
                    task.conn_retries += 1
                    continue
            # check data was received
            if task.task:
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
                try:
                    if task.ack:
                        await task.task.ack()
                    task.ack = True
                    task.reset()
                except (ConnectionRefusedError, NetworkError):
                    if task.conn_max_retries == task.conn_retries:
                        raise
                    await asyncio.sleep(task.conn_retry_countdown)
                    task.conn_retries += 1
                    continue
            await asyncio.sleep(task.timeout)
        task.shutdown()
