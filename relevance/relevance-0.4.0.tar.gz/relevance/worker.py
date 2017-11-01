"""
Relevance worker module.
"""

import abc
import signal
import typing
import threading
import multiprocessing
from queue import Queue
from queue import Empty


class InvalidWorkerStateError(RuntimeError):
    """
    Exception raised when the worker is in an invalid state for the requested operation.
    """
    pass


class Worker(object, metaclass=abc.ABCMeta):
    """
    Worker interface.
    """
    def __init__(self):
        """
        Initialize the worker.

        :param scope: the worker's signal queue.
        """
        self.scope = Queue()
        self.handles = {}
        self.parents = []
        self.children = []
        self.is_started = False

    @abc.abstractmethod
    def run(self):
        """
        Run the worker.
        """
        pass

    def add(self, worker: 'Worker'):
        """
        Add a child worker.

        :param worker: the child worker.
        """
        if self.is_started:
            raise InvalidWorkerStateError()

        worker.parents.append(self)
        self.children.append(worker)

    def signal(self, signal: str, **args):
        """
        Send a signal to the worker.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        if self.scope is None:
            return

        self.scope.put((signal, args))

    def emit(self, signal: str, **args):
        """
        Emit a signal down the worker's parents.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        for x in self.parents:
            x.signal(signal, **args)
            x.emit(signal, **args)

    def broadcast(self, signal: str, **args):
        """
        Broadcast a signal up to all the worker's children.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        for x in self.children:
            x.signal(signal, **args)
            x.broadcast(signal, **args)

    def bubble(self, signal: str, **args):
        """
        Bubble up a signal to the worker's parents and siblings.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        for x in self.parents:
            x.signal(signal, **args)
            x.broadcast(signal, **args)

    def trigger(self, signal: str, **args):
        """
        Trigger a signal to the worker itself and its children.

        :param signal: the signal to emit.
        :param args: the signal arguments.
        """
        self.signal(signal, **args)
        self.broadcast(signal, **args)

    def listen(self, signal: str, func: typing.Callable, **args):
        """
        Add a signal handler in the worker.

        :param signal: the signal to emit.
        :param func: a callable target to execute.
        :param args: arguments to pass to the callable.
        """
        if self.is_started:
            raise InvalidWorkerStateError()

        if signal not in self.handles:
            self.handles[signal] = []
        self.handles[signal].append((func, args))

    def execute(self, signal: str, **args):
        """
        Execute a signal event.

        :param signal: the signal to trigger.
        :param args: the signal arguments.
        """
        if signal in self.handles:
            for func, kwargs in self.handles[signal]:
                args = {**args, **kwargs}
                func(**args)

    def event_loop(self):
        """
        Worker event loop.
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
        """
        for x in self.children:
            x.start()

        if self.is_started:
            return

        self.is_started = True
        self.run()

    def stop(self, force: bool=False):
        """
        Stop the worker.

        :param force: whether to force stop the worker or not.
        """
        self.trigger('stop', force=force)

    def kill(self):
        """
        Kill the worker.
        """
        for x in self.children:
            x.kill()

        self.is_started = False
        while not self.scope.empty():
            self.scope.get()
            self.scope.task_done()

    def join(self):
        """
        Join the worker.
        """
        for x in self.children:
            x.join()


class WorkerProxy(object):
    """
    Worker proxy class.
    """
    def __init__(self, worker: Worker):
        """
        Initialize the proxy.

        :param worker: the worker object.
        """
        self.worker = worker

    def emit(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.emit(*args, **kwargs)

    def broadcast(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.broadcast(*args, **kwargs)

    def bubble(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.bubble(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.trigger(*args, **kwargs)

    def listen(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.listen(*args, **kwargs)

    def start(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.start(*args, **kwargs)

    def stop(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.stop(*args, **kwargs)

    def kill(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.kill(*args, **kwargs)

    def join(self, *args, **kwargs):
        """
        Overload method to the worker object.
        """
        self.worker.join(*args, **kwargs)


class SimpleWorker(Worker):
    """
    Simple worker implementation.
    """
    def run(self):
        """
        Run the worker.
        """
        signal.signal(signal.SIGINT, lambda *a: setattr(self, 'is_started', False))
        self.event_loop()

    def join(self):
        """
        Join the worker.
        """
        super().join()
        while self.is_started or not self.scope.empty():
            self.event_loop()
        self.scope = None


class ThreadWorker(Worker):
    def __init__(self):
        """
        Initialize the worker.
        """
        super().__init__()
        self.thread = None

    def run(self):
        """
        Run the worker.
        """
        if self.thread is not None:
            raise InvalidWorkerStateError()

        self.thread = threading.Thread(target=self.event_loop)
        self.thread.start()

    def kill(self):
        """
        Kill the worker.
        """
        if self.thread is None:
            raise InvalidWorkerStateError()

        self.thread.terminate()

    def join(self):
        """
        Join the worker.
        """
        if self.thread is None:
            raise InvalidWorkerStateError()

        super().join()
        self.thread.join()
        self.thread = None


class ProcessWorker(Worker):
    """
    Process worker implementation.
    """
    # The multiprocessing context type
    context_type = 'spawn'

    def __init__(self):
        """
        Initialize the worker.
        """
        super().__init__()
        self.process = None
        self.context = multiprocessing.get_context(self.context_type)
        self.scope = self.context.JoinableQueue()

    def run(self):
        """
        Run the worker.
        """
        if self.process is not None:
            raise InvalidWorkerStateError()

        self.process = self.context.Process(target=self.event_loop)
        self.process.start()

    def kill(self):
        """
        Kill the worker.
        """
        if self.process is None:
            raise InvalidWorkerStateError()

        for x in self.children:
            x.kill()

        self.process.terminate()

    def join(self):
        """
        Join the worker.
        """
        if self.process is None:
            raise InvalidWorkerStateError()

        super().join()
        self.process.join()
        self.process = None
        self.scope = None


class ForkedWorker(ProcessWorker):
    """
    Isolated process spawn worker implementation.
    """
    # The multiprocessing context type
    context_type = 'fork'
