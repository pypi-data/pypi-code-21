
import uuid
import logging_helper
from time import sleep
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool as _ThreadPool
from timingsutil.timers import Timeout

logging = logging_helper.setup_logging()


class ThreadPool(object):

    def __init__(self,
                 worker_threads=cpu_count()):

        """ Initialises the thread pool

        :param worker_threads: Number of threads in the thread pool, defaults to number of CPU's available.
        """

        self.id = uuid.uuid4()
        self.num_threads = worker_threads
        self._pool = None
        self._created = False  # Set termination flag
        self._in_progress = []

    def create(self):

        """ Enables the thread pool

        :return: N/A
        """

        if self._pool is None:
            logging.debug(u'Creating thread pool ({uuid}) with {n} threads...'.format(uuid=self.id,
                                                                                      n=self.num_threads))

            # Initialise the pool
            self._pool = _ThreadPool(processes=self.num_threads if self.num_threads > 1 else 2)

            # Set termination flag
            self._created = True

        else:
            logging.debug(u'Not creating pool, there is already an active instance!')

    def destroy(self):

        """ Closes and joins the thread pool.

        This is blocking until all tasks already submitted are complete.

        :return: N/A
        """

        if self._created:
            logging.info(u'Destroying thread pool ({uuid}), '
                         u'waiting for processes to complete...'.format(uuid=self.id))

            # Signal loop termination
            self._created = False

            # Wait for running processes to complete
            self._pool.close()
            self._pool.join()
            self._pool = None

            logging.info(u'Thread pool ({uuid}) destroyed!'.format(uuid=self.id))

    def submit_task(self,
                    func,
                    args=None,
                    kwargs=None):

        """ Add a task to the queue

        :param func:    The function to run in a thread
        :param args:    The args to pass to the function
        :param kwargs:  The kwargs to pass to the function
        :return:        multiprocessing.AsyncResult object for the task
        """

        async_result = None
        args = () if not args else args
        kwargs = {} if not kwargs else kwargs

        if self.active and self._pool is not None:
            # Pass item to worker thread
            async_result = self._pool.apply_async(func=func,
                                                  args=args,
                                                  kwds=kwargs)

            self._in_progress.append(async_result)

        return async_result

    def wait(self,
             wait_tasks=None,
             timeout=86400,
             poll_delay=1):

        """ Waits for the submitted tasks to complete.
            Note: this is blocking.

        :param wait_tasks:  list of multiprocessing.AsyncResult tasks to wait for.
                            If not provided it will be initialised to all tasks submitted to the pool.
        :param timeout:     Maximum time to wait for tasks to complete.  If not set waits 24 hours.
        :param poll_delay:  The delay between each check of the task statuses, default = 1 second.
        :return:            N/A
        """

        if wait_tasks is None:
            wait_tasks = self._in_progress

        # Setup timer
        timer = Timeout(seconds=timeout)

        complete = False

        while not complete and not timer.expired:
            if all(item.ready() for item in wait_tasks):
                complete = True

            sleep(poll_delay)

        # We are done so check result status and clear completed items from in progress!
        for item in wait_tasks:
            if item.ready():
                # If any downloads have raised an exception calling get() will raise the exception here!
                item.get()
                self._in_progress.remove(item)

    @property
    def active(self):
        return self._created


class ThreadPoolMixIn(object):

    def __init__(self,
                 worker_threads=cpu_count()):

        super(ThreadPoolMixIn, self).__init__()

        self._pool = ThreadPool(worker_threads)

    def open_pool(self):
        self._pool.create()

    def close_pool(self):
        self._pool.destroy()


class SingleUseThreadPool(object):

    def __init__(self,
                 worker_threads=cpu_count()):

        """ Initialise and create the thread pool """

        # Initialise thread pool
        self._pool = ThreadPool(worker_threads=worker_threads)
        self._pool.create()

        self._in_progress = []

    def submit_task(self,
                    func,
                    args=None,
                    kwargs=None):

        """ Add a task to the queue.

        :param func:    The function to run in a thread
        :param args:    The args to pass to the function
        :param kwargs:  The kwargs to pass to the function
        :return:        N/A
        """

        async_result = self._pool.submit_task(func,
                                              args=args,
                                              kwargs=kwargs)

        self._in_progress.append(async_result)

        return async_result

    def wait(self):

        """ Waits for the submitted tasks to complete and once complete destroys the pool.
            Note: this is blocking.

        :return: N/A
        """

        self._pool.wait(wait_tasks=self._in_progress)

        # Clean up thread pool
        self._pool.destroy()


if __name__ == '__main__':
    from random import randrange

    delays = [randrange(1, 10) for i in range(100)]

    def wait_delay(delay):
        logging.info(u'sleeping for {d} sec'.format(d=delay))
        sleep(delay)
        return delay

    # 1) Init a Thread pool with the desired number of threads
    pool = ThreadPool(10)
    pool.create()

    for i, d in enumerate(delays):
        # print the percentage of tasks placed in the queue
        logging.info('%.2f%c' % ((float(i)/float(len(delays)))*100.0, '%'))

        # 2) Add the task to the queue
        pool.submit_task(wait_delay, (d,))

    sleep(2)  # brief sleep to allow all delays to be submitted before destroying

    # 3) Wait for completion
    pool.destroy()
