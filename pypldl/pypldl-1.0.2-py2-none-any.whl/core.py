import urllib3
import logging
import shutil
import os
import Queue
import threading
from bs4 import BeautifulSoup

logger = logging.getLogger('core')

plugin_handlers = []

def register_plugin_module(module):
    """Register Task subclasses from a module"""
    for name in dir(module):
        if name.startswith('_'):
            continue
        obj = getattr(module, name)
        if isinstance(obj, type(Task)) and issubclass(obj, Task) and obj is not Task:
            plugin_handlers.append(obj)


class Task(object):
    """
    A high-level download task

    Attributes:
      dm -- DownloadManager running the instance (or None)
      outdir (optional) -- output directory
      base_url (optional) -- base URL for request helpers
      lock -- lock for synchronous accesses
      run_thread -- thread running the task

    Class attribute:
      handler_name -- name of the handler

    Tasks are run sequentially. The run() method can block.

    """

    def __init__(self):
        self.dm = None
        self.outdir = None
        self.lock = threading.RLock()
        self.run_thread = None

    @classmethod
    def from_uri(cls, uri):
        """Instantiate a task from a URI

        To be redefined by each Task subclass.
        Return None if URI is not handled.
        """
        for task_cls in plugin_handlers:
            task = task_cls.from_uri(uri)
            if task is not None:
                return task
        else:
            raise ValueError("no handler for '%s'" % uri)

    def run(self):
        """Run the task"""
        raise NotImplementedError()

    def progress(self):
        """Return task progress

        Return value is a (float, string) pair:
          float -- progress value, between 0 and 1
          string -- human progress status
        """
        raise NotImplementedError()


    def start(self, dm):
        """Start the task in background

        Parameters:
          dm -- DownloadManager instance

        """
        logger.info('task %s: starting', self)
        if self.dm is not None:
            raise RuntimeError("task already running")
        self.dm = dm
        self.run_thread = threading.Thread(target=self._thread_run, name='run-task')
        self.run_thread.daemon = True
        self.run_thread.start()

    def join(self, timeout=None):
        """Wait for the task to finish
        Return True if finished, False if still running.
        """
        if timeout > 0:
            self.run_thread.join(timeout)
        return not self.run_thread.isAlive()

    def _thread_run(self):
        """Run the task, wait for jobs to complete"""
        self.run()
        self.dm.queue.join()



    # helpers

    def outpath(self, *parts):
        """Return an output path"""
        return os.path.join(self.dm.outdir, self.outdir, *parts)

    def absolute_url(self, path):
        """Transform a URL or path to an absolute URL"""
        if '://' in path:
            return path
        return '{0}/{1}'.format(self.base_url, path)

    def request(self, path, **kw):
        """Fetch a path or URL as a BeautifulSoup object"""
        return self.dm.request(self.absolute_url(path), **kw)

    def request_soup(self, path):
        """Fetch a path or URL as a BeautifulSoup object"""
        return self.dm.request_soup(self.absolute_url(path))

    def download(self, path, output, **kw):
        """Download a path or URL to a file"""
        return self.dm.download(self.absolute_url(path), output, **kw)


class DownloadManager(object):
    """
    Manage download tasks

    Attributes:
      pool -- urllib3.PoolManager instance
      workers -- list of worker threads
      queue -- priority queue of jobs to process
      outdir -- base output directory

    Queue values follow this format: (priority, callback, args).
    Priority is expected to be a tuple, to allow hierarchical priorities.

    """

    # some servers requires a User-Agent
    default_headers = {'User-Agent': 'dummy'}

    def __init__(self, workers=10, retries=5, timeout=10, connection_pools=10):
        """Create a download manager

        Parameters:
          workers -- number of parallel jobs
          connection_pools -- number of connection pools
          retries -- number of retries
          timeout -- pool total timeout, in seconds

        """
        self.pool = urllib3.PoolManager(
                num_pools=connection_pools,
                maxsize=workers,
                retries=urllib3.Retry(retries),
                timeout=urllib3.Timeout(timeout),
                headers=self.default_headers,
                )
        self.queue = Queue.PriorityQueue()
        self.workers = None
        self.outdir = ''

        if self.workers is not None:
            raise RuntimeError("download manager already started")
        self.workers = []
        logger.debug("starting download manager")
        for i in range(workers):
            worker = threading.Thread(target=self._run_worker, name='worker-%d' % i)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)


    def add_job(self, priority, job, args=None):
        """Enqueue a job execution"""
        if args is None:
            args = ()
        logger.debug("add job with priority %r", priority)
        self.queue.put((priority, job, args))


    def _run_worker(self):
        """Worker thread routine"""
        q = self.queue
        try:
            while True:
                try:
                    priority, job, args = q.get()
                except Queue.Empty:
                    continue
                try:
                    job(*args)
                finally:
                    q.task_done()
        except Exception:
            logger.error("worker %s failed", threading.current_thread().name, exc_info=True)


    def request(self, url, method='GET', **kw):
        """Fetch a URL"""
        # request() ignores headers() at pool level
        if 'headers' not in kw:
            kw['headers'] = self.default_headers
        return self.pool.request(method, url, preload_content=False, **kw)

    def request_soup(self, url, **kw):
        """Fetch a URL as a BeautifulSoup object"""
        return BeautifulSoup(self.request(url, **kw).data, 'html5lib')

    def download(self, url, output, method='GET', **kw):
        """Download a URL to a file"""
        # create directory if needed
        outdir = os.path.dirname(output)
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        r = self.pool.urlopen(method, url, preload_content=False, **kw)
        try:
            with open(output, 'wb') as fout:
                shutil.copyfileobj(r, fout)
        except:
            # remove downloaded file on error
            try:
                os.unlink(output)
            except IOError:
                pass
            raise
        finally:
            r.release_conn()


