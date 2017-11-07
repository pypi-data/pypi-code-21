"""
This module provides some utilities and classes to implement multiprocessing workloads.
"""

import abc
import signal
import typing
import threading
import multiprocessing
from queue import Queue
from queue import Empty

from relevance import loggers


# Logging
logger = loggers.getLogger('relevance.worker')


class Worker(object, metaclass=abc.ABCMeta):
    """
    This interface allows to implement different worker types, such as threaded workers,
    process workers or network workers.
    """
    def __init__(self):
        """
        :var scope: contains the signal queue for the worker.
        :var children: contains the list of children workers for this worker.
        :var is_started: whether the worker is started or not.
        """
        self.scope = Queue()
        self.handles = {}
        self.parents = []
        self.children = []
        self.is_started = False
        logger.debug('init', inst=self)

    @abc.abstractmethod
    def run(self):
        """
        This is the method that needs to be implemented based on the worker type.
        For threaded workers per example, this method will spawn a thread and start it.
        """
        pass

    def add(self, worker: 'Worker'):
        """
        Add a child worker.

        Child workers can emit signals down to their parents or receive signal broadcasts
        from their parents.

        :param worker: the child worker object.
        :raises: :class:`InvalidWorkerStateError`: if the worker is started. A worker's
            hierarchy cannot be modified once it's started. It needs to be stopped first,
            then it can be modified.
        """
        if self.is_started:
            raise InvalidWorkerStateError()

        worker.parents.append(self)
        self.children.append(worker)
        logger.debug('add', inst=self, worker=worker)

    def signal(self, signal: str, **args):
        """
        Send a signal to the worker.

        This only sends a signal to the current worker. To send signals up or down the
        worker's hierarchy, see :meth:`Worker.emit`, :meth:`Worker.broadcast` and
        :meth:`Worker.trigger`.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        if self.scope is None:
            return

        logger.info('signal', inst=self, signal=signal, args=args)
        self.scope.put((signal, args))

    def emit(self, signal: str, **args):
        """
        Emit a signal to the worker's parents.

        This method does not send a signal to the current worker however, only to
        its parents.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        logger.debug('emit', inst=self, signal=signal, args=args)
        for x in self.parents:
            x.signal(signal, **args)
            x.emit(signal, **args)

    def broadcast(self, signal: str, **args):
        """
        Broadcast a signal up to all the worker's children.

        This method does not send a signal to the current worker, only its children.
        To send a signal to the current worker and its children as well, use
        :meth:`Worker.trigger`.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        logger.debug('broadcast', inst=self, signal=signal, args=args)
        for x in self.children:
            x.signal(signal, **args)
            x.broadcast(signal, **args)

    def trigger(self, signal: str, **args):
        """
        Send a signal to the current worker and all of its children.

        This method sends a signal to the current worker's children and itself.
        To only send a signal to the children, use :meth:`Worker.broadcast`.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        logger.debug('trigger', inst=self, signal=signal, args=args)
        self.signal(signal, **args)
        self.broadcast(signal, **args)

    def listen(self, signal: str, func: typing.Callable, **args):
        """
        Add a signal handler in the worker.

        :param signal: the signal to handle.
        :param func: a callable to execute when the signal is received.
        :param args: default arguments to pass to the callable. Whenever the specified
            signal is received, the arguments specified here will be passed to all
            handlers whether they were in the payload or not.
        :raises: :class:`InvalidWorkerStateError`: if the worker is started. A worker's
            handlers cannot be modified once it's started. It needs to be stopped first,
            then it can be modified.
        """
        if self.is_started:
            raise InvalidWorkerStateError()

        logger.debug('listen', inst=self, signal=signal, func=func, args=args)
        if signal not in self.handles:
            self.handles[signal] = []
        self.handles[signal].append((func, args))

    def execute(self, signal: str, **args):
        """
        Execute all registered handlers for the specified signal in the current worker.

        This method is mostly use internally. To generate a signal, use :meth:`Worker.signal`.

        :param signal: the signal to trigger.
        :param args: the signal arguments.
        """
        if signal in self.handles:
            for func, kwargs in self.handles[signal]:
                args = {**args, **kwargs}
                func(**args)

    def event_loop(self):
        """
        The worker event loop.

        This method is mostly used internally. You should not override it unless you know
        what you're doing. It takes care of receiving and handling the multiple signals
        that are sent to the worker, and cleaning up after it stops.
        """
        self.execute('worker_start')

        while self.is_started or not self.scope.empty():
            self.execute('loop_start')

            try:
                signal, args = self.scope.get(timeout=0.001)
                self.scope.task_done()
                self.execute(signal, **args)

                if signal == 'stop':
                    if args['force']:
                        break
                    else:
                        self.is_started = False
            except Empty:
                pass

            self.execute('loop_end')

        self.is_started = False
        self.execute('worker_end')

    def start(self):
        """
        Start the worker.

        If the worker is already started, this has no effect.
        """
        for x in self.children:
            x.start()

        if self.is_started:
            return

        logger.debug('start', inst=self)
        self.is_started = True
        self.run()

    def stop(self, force: bool=False):
        """
        Stop the worker.

        When requesting a worker to stop, it will stop only when its event queue is
        empty. Using `force` will avoid that and the worker will be stopped as soon as
        the current event, if any, finishes.

        If the worker is already stopped, this has no effect.

        :param force: whether to force stop the worker or not.
        """
        logger.debug('stop', inst=self, force=force)
        self.trigger('stop', force=force)

    def kill(self):
        """
        Kill the worker.

        This should be rarely used, but can be useful to terminating stuck workers and
        the likes. Unlike :meth:`Worker.stop`, this method does not perform any clean up.
        Caution is advised.
        """
        logger.debug('kill', inst=self)
        for x in self.children:
            x.kill()

        self.is_started = False
        while not self.scope.empty():
            self.scope.get()
            self.scope.task_done()

    def join(self):
        """
        Join the worker.

        Calling this method will wait the current worker has stopped, as well as
        all its children. Make sure to call :meth:`Worker.stop` first.
        """
        logger.debug('join', inst=self)
        for x in self.children:
            x.join()


class WorkerProxy(object):
    """
    This class is useful for implementing workers within other objects. It proxies
    the :class:`Worker` interface through composition.
    """
    def __init__(self, worker: Worker):
        """
        :param worker: the worker object to use for the instance.
        """
        self.worker = worker

    def emit(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.emit`.
        """
        self.worker.emit(*args, **kwargs)

    def broadcast(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.broadcast`.
        """
        self.worker.broadcast(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.trigger`.
        """
        self.worker.trigger(*args, **kwargs)

    def listen(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.listen`.
        """
        self.worker.listen(*args, **kwargs)

    def start(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.start`.
        """
        self.worker.start(*args, **kwargs)

    def stop(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.stop`.
        """
        self.worker.stop(*args, **kwargs)

    def kill(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.kill`.
        """
        self.worker.kill(*args, **kwargs)

    def join(self, *args, **kwargs):
        """
        Implementation of :meth:`Worker.join`.
        """
        self.worker.join(*args, **kwargs)


class SimpleWorker(Worker):
    """
    This simple worker implementation runs in the current thread and does not
    multiprocess at all. Starting it will block the current process.

    However, when the current process receives the `SIGINT` signal, the worker
    will generate a `stop` signal and be allowed to stop.
    """
    def run(self):
        """
        Implementation of :meth:`Worker.run`.
        """
        signal.signal(signal.SIGINT, lambda *a: setattr(self, 'is_started', False))
        self.event_loop()

    def join(self):
        """
        Implementation of :meth:`Worker.join`.
        """
        super().join()
        while self.is_started or not self.scope.empty():
            self.event_loop()
        self.scope = None


class ThreadWorker(Worker):
    """
    This worker class uses a thread for multiprocessing.
    """
    def __init__(self):
        """
        .. init
        """
        super().__init__()
        self.thread = None

    def run(self):
        """
        Implementation of :meth:`Worker.run`.
        """
        if self.thread is not None:
            raise InvalidWorkerStateError()

        self.thread = threading.Thread(target=self.event_loop)
        self.thread.start()

    def kill(self):
        """
        Implementation of :meth:`Worker.kill`.
        """
        if self.thread is None:
            raise InvalidWorkerStateError()

        logger.debug('kill', inst=self)
        self.thread.terminate()

    def join(self):
        """
        Implementation of :meth:`Worker.join`.
        """
        if self.thread is None:
            raise InvalidWorkerStateError()

        super().join()
        self.thread.join()
        self.thread = None


class ProcessWorker(Worker):
    """
    This worker type uses spawned processes for multiprocessing. Spawned process
    do not shared any resource with their parents: they are isolated.
    """
    context_type = 'spawn'
    """ :const: The multiprocessing context type for the worker. """

    def __init__(self):
        """
        .. init
        """
        super().__init__()
        self.process = None
        self.context = multiprocessing.get_context(self.context_type)
        self.scope = self.context.JoinableQueue()

    def run(self):
        """
        Implementation of :meth:`Worker.run`.
        """
        if self.process is not None:
            raise InvalidWorkerStateError()

        self.process = self.context.Process(target=self.event_loop)
        self.process.start()

    def kill(self):
        """
        Implementation of :meth:`Worker.kill`.
        """
        if self.process is None:
            raise InvalidWorkerStateError()

        logger.debug('kill', inst=self)
        for x in self.children:
            x.kill()

        self.process.terminate()

    def join(self):
        """
        Implementation of :meth:`Worker.join`.
        """
        if self.process is None:
            raise InvalidWorkerStateError()

        super().join()
        self.process.join()
        self.process = None
        self.scope = None


class ForkedWorker(ProcessWorker):
    """
    Like a :class:`ProcessWorker`, but forked workers can actually share resources
    with their parents, such as file descriptors.
    """
    context_type = 'fork'
    """ :const: The multiprocessing context type for the worker. """


class InvalidWorkerStateError(RuntimeError):
    """
    This exception is raised when attempting to perform an operation, with the worker
    not being in a valid state for that specific operation. Per example, attempting
    to add a new signal handler to a started worker will cause this error.
    """
    pass
