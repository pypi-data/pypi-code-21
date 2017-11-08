import time

from async_task_processor import ATP
from async_task_processor.processors import PeriodicProcessor
from examples import logger


# first test function
def test_func_one(sleep_time, word):
    """

    :type sleep_time: int
    :type word: str
    :return:
    """
    logger.info('start working')
    time.sleep(sleep_time)
    logger.info('Job is done. Word is: %s' % word)


# second test function
def test_func_second(sleep_time, word):
    """

    :type sleep_time: int
    :type word: str
    :return:
    """
    logger.info('start working')
    time.sleep(sleep_time)
    logger.info('Job is done. Word is: %s' % word)


# third function with exception
def test_func_bad(self, sleep_time, word):
    """

    :type self: async_task_processor.Task
    :type sleep_time: int
    :type word: str
    :return:
    """
    logger.info('start working')
    try:
        a = 1 / 0
    except ZeroDivisionError:
        # optionally you can overload max_retries and retry_countdown here
        self.retry()
    time.sleep(sleep_time)
    logger.info('Job is done. Word is: %s' % word)


atp = ATP(asyncio_debug=True)
task_processor = PeriodicProcessor(atp=atp)

# Add function to task processor
task_processor.add_task(test_func_one, args=[5, 'first hello world'], max_workers=5, timeout=1,
                        max_retries=5, retry_countdown=1)

# Add one more function to task processor
task_processor.add_task(test_func_second, args=[3, 'second hello world'], max_workers=5, timeout=1,
                        max_retries=5, retry_countdown=1)

# Add one more bad function with exception. This function will raise exception and will retry it,
# then when retries exceeded, workers of this func will stop one by one with exception MaxRetriesExceeded
# bind option make Task as self argument
task_processor.add_task(test_func_bad, args=[3, 'second hello world'], bind=True, max_workers=2, timeout=1,
                        max_retries=3, retry_countdown=3)

# Start async-task-processor
atp.start()
