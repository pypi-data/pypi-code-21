import os
import sys
import errno
import threading
import queue
import steov

class Task (threading.Thread):
    def __init__ (self, method, *args, **kwargs):
        super().__init__(target=self.__run)
        self.__method = method
        self.__args = args
        self.__kwargs = kwargs
        self.success = None
        self.result = None
        self.stacktrace = None
        self.start()

    def __run (self):
        try:
            result = self.__method(*self.__args, **self.__kwargs)
        except Exception:
            self.success = False
            self.result = None
            self.stacktrace = steov.format_exc()
        else:
            self.success = True
            self.result = result
            self.stacktrace = None

    def is_done (self):
        return self.success is not None

class ThreadPool:
    def __init__ (self, size):
        if not isinstance(size, int):
            raise ValueError("size: expected int, got " + type(size).__name__)
        if size <= 0:
            raise ValueError("size: expected > 0, got " + size)
        self._size = size
        self._state_lock = threading.Lock()
        # states: init starting started stopping stopped
        self._state = "init"
        self._prev_id = 0

    def _next_id (self):
        with self._id_lock:
            self._prev_id += 1
            return self._prev_id

    def _thread_target (self):
        while True:
            t = self._queue.get()
            try:
                priority, item = t
                if item is None:
                    self._queue.put(t)
                    break
                method, args, kwargs = item
                try:
                    method(*args, **kwargs)
                except Exception:
                    print(steov.format_exc(), end="", file=sys.stderr)
            finally:
                self._queue.task_done()

    def start (self):
        with self._state_lock:
            if self._state != "init":
                if self._state in { "starting" , "started" }:
                    raise ValueError("ThreadPool has already started")
                if self._state in { "stopping", "stopped" }:
                    raise ValueError("ThreadPool has already stopped")
                # this should never happen. maybe log an error?
                raise ValueError("ThreadPool state: must be init")
            self._state = "starting"

        self._queue = queue.PriorityQueue()
        self._threads = []
        self._id_lock = threading.Lock()
        for _ in range(self._size):
            thread = threading.Thread(target=self._thread_target)
            thread.start()
            self._threads.append(thread)

        # pretty sure assignments are atomic, so this doesn't need to be locked
        self._state = "started"

    def add (self, method, *args, **kwargs):
        with self._state_lock:
            if self._state != "started":
                if self._state in { "init" , "starting" }:
                    raise ValueError("ThreadPool has not yet started")
                if self._state in { "stopping", "stopped" }:
                    raise ValueError("ThreadPool has already stopped")
                # this should never happen. maybe log an error?
                raise ValueError("ThreadPool state: must be init")

            # this needs to be in the state_lock block to prevent race
            # conditions with stop() putting `None` on the queue????
            self._queue.put((self._next_id(), (method, args, kwargs)))

    def wait (self):
        with self._state_lock:
            if self._state not in { "started" , "stopping" , "stopped" }:
                raise ValueError("ThreadPool has not yet started")
        self._queue.join()

    def stop (self):
        # TODO allow multiple stops even if already stopping or stopped?
        with self._state_lock:
            if self._state != "started":
                if self._state in { "init" , "starting" }:
                    raise ValueError("ThreadPool has not yet started")
                if self._state == "stopping":
                    raise ValueError("ThreadPool is already stopping")
                if self._state == "stopped":
                    raise ValueError("ThreadPool is already stopped")
            self._state = "stopping"

        self._queue.join()
        self._queue.put((self._next_id(), None))
        for thread in self._threads:
            thread.join()
        self._queue.get()
        self._queue.task_done()

        self._state = "stopped"

    def __enter__ (self):
        self.start()
        return self

    def __exit__ (self, type, value, tb):
        # TODO wait first? in case an exception happens while waiting and we
        # want to abort? but abort isn't finished yet
        self.stop()

class IpLock:
    def __init__ (self, lock_file):
        self._lock_file = lock_file
        os.makedirs(os.path.dirname(os.path.abspath(self._lock_file)), exist_ok=True)
        self.acquired_lock = None

    def __enter__ (self):
        try:
            os.mknod(self._lock_file)
        except OSError as er:
            if er.errno == errno.EEXIST:
                self.acquired_lock = False
            else:
                raise
        else:
            self.acquired_lock = True
        return self.acquired_lock

    def __exit__ (self, ex_type, ex_value, ex_traceback):
        if self.acquired_lock:
            os.remove(self._lock_file)
