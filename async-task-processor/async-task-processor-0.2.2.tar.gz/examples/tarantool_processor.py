import asyncio
import time

import asynctnt
import asynctnt_queue

from async_task_processor import ATP
from async_task_processor.processors import TarantoolProcessor
from examples import logger

TARANTOOL_QUEUE = 'test_queue'
TARANTOOL_HOST = 'localhost'
TARANTOOL_PORT = 3301
TARANTOOL_USER = None
TARANTOOL_PASS = None


def put_messages_to_tarantool(messages_count=1, tube_name='test_queue', host='localhost', port=3301, user=None,
                              password=None):
    """Put some test messages to tarantool queue

    :param messages_count: messages number to put in queue
    :param tube_name: tarantool queue name
    :type tube_name: str
    :param host: tarantool host
    :param port: tarantool port
    :param user: tarantool user
    :param password: tarantool password
    :return:
    """

    async def put_jobs():
        conn = asynctnt.Connection(host=host, port=port, username=user, password=password)
        await conn.connect()
        queue = asynctnt_queue.Queue(conn)
        tube = queue.tube(tube_name)
        [await tube.put(dict(num=i, first_name='Jon', last_name='Smith')) for i in range(messages_count)]
        await conn.disconnect()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(put_jobs()))
    loop.close()


# Let's put 100 messages to tarantool
put_messages_to_tarantool(messages_count=100, tube_name=TARANTOOL_QUEUE, host=TARANTOOL_HOST, port=TARANTOOL_PORT,
                          user=TARANTOOL_USER, password=TARANTOOL_PASS)


# Test function
def test_func(self, sleep_time, word):
    """

    :type self: async_task_processor.TarantoolTask
    :type sleep_time: int
    :type word: str
    :return:
    """
    logger.info('start working')
    time.sleep(sleep_time)
    logger.info('Job is done. Word is %s. Data is %s. ' % (word, self.data))


atp = ATP(asyncio_debug=True)
task_processor = TarantoolProcessor(atp=atp, host=TARANTOOL_HOST, port=TARANTOOL_PORT, user=TARANTOOL_USER,
                                    password=TARANTOOL_PASS, connection_max_retries=3, connection_retry_countdown=3)

# Add function to task processor. Tarantool data from queue will be in `self` argument in function. 20 parallel workers
# will be started.
task_processor.add_task(foo=test_func, queue=TARANTOOL_QUEUE, args=[1, 'hello world'], bind=True, max_workers=20,
                        max_retries=5, retry_countdown=1)
# Start async-task-processor
atp.start()
