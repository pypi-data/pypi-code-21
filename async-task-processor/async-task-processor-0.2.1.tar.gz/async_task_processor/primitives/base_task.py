import json
import sys
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

from async_task_processor.exceptions import MaxRetriesExceedException, RetryException


class BaseTask(object):
    loop = None
    type = None
    id = None
    name = None
    coroutine_future = None
    app = None
    processor = None
    foo = None
    executor = None
    args = None
    bind = None
    timeout = None
    max_retries = None
    retries = 0

    def __init__(self, loop, task_type, foo, args, bind, timeout, max_retries, retry_countdown, name):
        """

        :type loop: asyncio.AbstractEventLoop
        :param task_type:
        :param foo:
        :param args:
        :param bind:
        :param timeout:
        :param max_retries:
        """
        self.name = name or foo.__name__
        self.loop = loop
        self.type = task_type
        self.id = uuid.uuid4()
        self.foo = foo
        self.args = args
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.bind = bind
        self.timeout = timeout or 0.01
        self.max_retries = max_retries or 0
        self.retry_countdown = retry_countdown or 1
        self.exception = None

    def retry(self, max_retries=None, retry_countdown=None):
        """Retry task execution

        :param max_retries:
        :param retry_countdown:
        :return:
        """
        if max_retries:
            self.max_retries = max_retries
        if retry_countdown:
            self.retry_countdown = retry_countdown
        if self.retries == self.max_retries:
            raise MaxRetriesExceedException(
                'max retries exceeded for exception {exception}, traceback:\n {traceback}'.format(
                    exception=sys.exc_info()[0], traceback=traceback.format_exc()))
        self.retries += 1
        raise RetryException(
            'trying to retry task on exception: {exception}. Retry #{retry}, traceback:\n {traceback}'.format(
                exception=repr(sys.exc_info()[0]), retry=self.retries, traceback=traceback.format_exc()))

    def set_future(self, future):
        """

        :type future: asyncio.Future
        :return:
        """
        self.coroutine_future = future

    def cancel(self):
        self.remove()
        self.coroutine_future.cancel()

    def remove(self):
        self.app.tasks.remove(self)
        self.processor.tasks.remove(self)

    def set_app(self, atp):
        """

        :type atp: async_task_processor.atp.ATP
        :return:
        """
        self.app = atp
        self.app.add_tasks(*[self])

    def set_processor(self, processor):
        """

        :type processor: async_task_processor.processors.base_processor.BaseProcessor
        :return:
        """
        self.processor = processor

    def shutdown(self):
        self.executor.shutdown()

    def as_dict(self):
        params = {arg: getattr(self, arg) for arg in self.__dict__ if
                  not arg.startswith('_') and not callable(getattr(self, arg))
                  and isinstance(getattr(self, arg), (int, str, float))}
        params['id'] = str(self.id)
        return params

    def __str__(self):
        return str(self.as_dict())

    def as_json(self):
        return json.dumps(self.as_dict())
