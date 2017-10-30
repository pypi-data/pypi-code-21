import asyncio
import importlib
import socket
import sys
import time

import asynctnt
import asynctnt_queue
import tarantool

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
        tube = asynctnt_queue.Queue(conn).tube(tube_name)
        [await tube.put(dict(num=i, first_name='Jon', last_name='Smith')) for i in range(messages_count)]
        await conn.disconnect()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(put_jobs()))
    loop.close()


# Let's put 100 messages to tarantool
put_messages_to_tarantool(messages_count=100, tube_name=TARANTOOL_QUEUE, host=TARANTOOL_HOST, port=TARANTOOL_PORT,
                          user=TARANTOOL_USER, password=TARANTOOL_PASS)


# Create tube in queue for manage workers
def create_tube(tube_name):
    try:
        t = tarantool.connect(host=TARANTOOL_HOST, port=TARANTOOL_PORT, user=TARANTOOL_USER,
                              password=TARANTOOL_PASS)
        t.call("queue.create_tube", (tube_name, 'fifo', {'if_not_exists': True}))
    except tarantool.error.DatabaseError as e:
        if e.args[0] == 32:
            pass
        else:
            raise


# Test function
def test_func(self, sleep_time, word):
    """

    :type self: async_task_processor.TarantoolTask
    :type sleep_time: int
    :type word: str
    :return:
    """
    logger.info('Start working')
    time.sleep(sleep_time)
    logger.info('Job is done. Word is %s. Data is %s. ' % (word, self.data))


# Function for import functions
def func_import(foo_path):
    path_list = foo_path.split('.')
    func_name = path_list.pop()
    m = importlib.import_module('.'.join(path_list)) if path_list else sys.modules[__name__]
    func = getattr(m, func_name)
    return func


# Function for manage workers
def add_task(self, tp):
    """

    :type self: async_task_processor.primitives.TarantoolTask
    :type tp: TarantoolProcessor
    :return:
    """
    if self.data['command'] == 'stop':
        tp.stop(task_name=self.data['foo'], workers_count=self.data['max_workers'], leave_last=False)
        self.app.logger.info("%d workers was deleted from task %s" % (self.data['max_workers'], self.data['foo']))
    elif self.data['command'] == 'start':
        tp.add_task(foo=func_import(self.data['foo']), queue=TARANTOOL_QUEUE, args=[1, 'message from new worker'],
                    bind=True, max_workers=self.data['max_workers'], name=self.data['foo'])
        self.app.logger.info("Added %d workers for task %s" % (self.data['max_workers'], self.data['foo']))
    elif self.data['command'] == 'info':
        [logger.info(task.as_json()) for task in self.app.tasks]
    else:
        self.app.logger.info("Unknown command %s" % self.data['command'])


# get host ip
ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
    [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
     [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0].replace('.', '_')

# manage tube name
control_tube_name = 'control_queue_%s' % ip
logger.info("control tube is %s" % control_tube_name)

# create tube for manage workers
create_tube(control_tube_name)

atp = ATP(asyncio_debug=True, logger=logger)

task_processor = TarantoolProcessor(atp=atp, host=TARANTOOL_HOST, port=TARANTOOL_PORT, user=TARANTOOL_USER,
                                    password=TARANTOOL_PASS, connection_max_retries=3, connection_retry_countdown=3)

# Add function to task processor. Tarantool data from queue will be in `self` argument in function. 20 parallel workers
# will be started.
task_processor.add_task(foo=test_func, queue=TARANTOOL_QUEUE, args=[1, 'hello world'], bind=True, max_workers=20,
                        max_retries=5, retry_countdown=1)

# Add task for listen manage tube commands. In this case if you start your app on different hosts,
# you would control all host, because ip in control queue and different queues will be created for each host.
# You can try to manage workers from tarantool console. Example command:
# queue.tube.control_queue_<your ip>:put({ foo='test_func', command = 'start', max_workers = 2})
task_processor.add_task(foo=add_task, queue=control_tube_name, args=[task_processor], bind=True)

# Start async-task-processor
atp.start()
