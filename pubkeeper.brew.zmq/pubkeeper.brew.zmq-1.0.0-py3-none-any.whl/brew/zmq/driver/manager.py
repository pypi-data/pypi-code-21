"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import zmq
from tornado.ioloop import PeriodicCallback
from zmq.eventloop import ioloop

from threading import RLock, Thread
from queue import Queue as TasksQueue, Empty

from pubkeeper.utils.logging import get_logger
from pubkeeper.utils.interface import is_interface, get_first_address, \
    InvalidInterface
from pubkeeper.brew.zmq.driver import ZMQSettings
from pubkeeper.brew.zmq.driver.queue import ZMQQueue
from pubkeeper.brew.zmq.driver.listener import ZMQListener
from pubkeeper.brew.zmq.driver.encryption import \
    ZMQServerEncryptionContext, ZMQServerEncryption, \
    ZMQClientEncryptionContext, ZMQClientEncryption


class InvalidQueue(Exception):
    pass


class InvalidListener(Exception):
    pass


class TaskItem(object):
    def __init__(self, target=None, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return "target: {}".format(self.target.__name__)


class ZMQManager(object):

    """The class that manages the interface with zmq functionality
    """
    _TERMINATION_TIMEOUT = 2

    def __init__(self):
        """ Initializes the manager.
        """
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)

        self._zmq_context = None
        self._queues_lock = RLock()
        self._queues = []
        self._listeners_lock = RLock()
        self._listeners = []

        # encryption setup
        self._publisher_encryption = None
        self._subscriber_encryption = None

        # zmq tasks execute in the ioloop running-thread
        self._ioloop_thread = None
        self._ioloop = None
        self._tasks_queue = TasksQueue()

    def configure(self, context):
        """ Configures zmq manager

        Args:
            context (dict): brew settings
        """

        # determine if ip_address is to be overriden
        if "ip_interface" in context and context["ip_interface"] is not None:
            try:
                interface_exists = is_interface(context["ip_interface"])
            except ImportError:   # pragma: no cover
                msg = "'ip_interface' setting requires the 'netifaces' " \
                      "python package"
                self.logger.exception(msg)
                raise ImportError(msg)

            if interface_exists:
                ip_address = get_first_address(context["ip_interface"])
                if ip_address:
                    # override if an address is returned
                    context["ip_address"] = ip_address
                else:
                    raise InvalidInterface(
                        "Interface: '{0}' does not have a valid address "
                        "assigned".format(context["ip_interface"]))
            else:
                raise InvalidInterface("Interface: '{0}' is not available".
                                       format(context["ip_interface"]))

        # override local setting with context incoming setting when provided
        non_casting_types = [type(None), str]
        for setting in ZMQSettings.keys():
            if setting in context:
                _type = type(ZMQSettings[setting])
                if _type in non_casting_types:
                    ZMQSettings[setting] = context[setting]
                else:
                    # cast incoming value to known type
                    ZMQSettings[setting] = _type(context[setting])

    def start(self):
        """ Starts the manager.
        """
        # create ioloop where all listener and zmq tasks will run
        self._ioloop = ioloop.IOLoop()
        # start worker thread
        self._ioloop_thread = Thread(target=self._worker,
                                     name="ZMQ Worker Thread")
        self._ioloop_thread.start()
        # execute _start in it
        self._tasks_queue.put(
            TaskItem(self._start))

    def stop(self):
        """ Stops the manager.
        """
        self._tasks_queue.put(
            TaskItem(self._stop))

        # wait for all tasks to be executed
        self._tasks_queue.join()
        # cause ioloop thread to end
        self._ioloop.stop()
        # wait for thread termination
        self._ioloop_thread.join(self._TERMINATION_TIMEOUT)
        if self._ioloop_thread.is_alive():
            self.logger.warning(
                'After {} seconds zmq tasks thread is still alive'.
                format(self._TERMINATION_TIMEOUT))  # pragma: no cover

    def create_queue(self, context=None):
        """ Creates a queue for sending messages.

        Returns:
            queue (ZMQQueue instance)

        Raises:
            InvalidQueue: if a queue with given name already exists.
        """
        queue = ZMQQueue(context)
        self._tasks_queue.put(
            TaskItem(self._connect_queue, queue))
        # wait for execution
        self._tasks_queue.join()

        # register queue
        with self._queues_lock:
            self._queues.append(queue)

        return queue

    def delete_queue(self, queue):
        """ Closes and deletes a queue.

        Args:
            queue: ZMQQueue instance

        Raises:
            InvalidQueue: if a queue with that name doesn't exist.
        """
        with self._queues_lock:
            if queue in self._queues:
                self._tasks_queue.put(
                    TaskItem(self._close_queue, queue))
                self._queues.remove(queue)
            else:
                raise InvalidQueue("ZMQQueue {0} does not exists".format(queue))

    def create_listener(self, publisher_url, handler):
        """ Creates a listener.

        Args:
            publisher_url (string): ZMQListener url
            handler (callback method): Message receiving method

        Raises:
            InvalidListener: if a listener with given url already exists.
        """
        listener = ZMQListener(publisher_url, handler, self._ioloop)
        self._tasks_queue.put(
            TaskItem(self._connect_listener, listener))

        # wait for execution
        self._tasks_queue.join()

        # save listener
        with self._listeners_lock:
            self._listeners.append(listener)

        return listener

    def delete_listener(self, listener):
        """ Closes and deletes a listener.

        Args:
            listener: ZMQListener instance

        Raises:
            InvalidListener: if given listener doesn't exist.
        """
        with self._listeners_lock:
            if listener in self._listeners:
                self._tasks_queue.put(
                    TaskItem(self._close_listener, listener))
                self._listeners.remove(listener)
                return

        raise InvalidListener("ZMQListener does not exists")

    def send(self, queue, signals):
        self._tasks_queue.put(
            TaskItem(self._send, queue, signals))

    def _start(self):
        self._zmq_context = zmq.Context(ZMQSettings["max_io_thread_count"])
        self._zmq_context.set(zmq.MAX_SOCKETS, ZMQSettings["max_sockets"])
        self.logger.info("Library socket count allowed: {0}".format(
            self._zmq_context.get(zmq.MAX_SOCKETS)))

        # setup encryption functionality
        self._publisher_encryption = ZMQServerEncryption()
        self._publisher_encryption.configure(
            ZMQServerEncryptionContext(
                self._zmq_context,
                ZMQSettings["allowed_ip_addresses"],
                ZMQSettings["publisher_public_keys_dir"],
                ZMQSettings["publisher_server_secret_cert"]))
        self._publisher_encryption.start()

        self._subscriber_encryption = ZMQClientEncryption()
        self._subscriber_encryption.configure(
            ZMQClientEncryptionContext(
                ZMQSettings["publisher_server_public_cert"],
                ZMQSettings["subscriber_client_secret_cert"]))

    def _stop(self):
        """ Cleans up manager resources.

        Closes all listeners and queues created through this manager in case
        they were not previously closed, and cleans up manager attributes.
        """
        # close "outstanding" listeners (subscribers)
        with self._listeners_lock:
            for listener in self._listeners:
                try:
                    listener.close()
                except Exception:  # pragma: no cover
                    self.logger.exception(
                        "During stop attempting to close "
                        "listener connection")   # pragma: no cover
            self._listeners = []

        # close queues (publishers)
        with self._queues_lock:
            for queue in self._queues:
                try:
                    queue.close()
                except Exception:  # pragma: no cover
                    self.logger.exception(
                        "During stop attempting to close "
                        "queue connection")  # pragma: no cover
            self._queues = []

        if self._publisher_encryption:
            self._publisher_encryption.stop()

        if self._zmq_context:
            self._zmq_context.term()
            self._zmq_context = None

    def _connect_queue(self, queue):
        queue.connect(self._zmq_context, self._publisher_encryption)

    def _close_queue(self, queue):
        queue.close()

    def _connect_listener(self, listener):
        listener.connect(self._zmq_context, self._subscriber_encryption)

    def _close_listener(self, listener):
        listener.close()

    @staticmethod
    def _send(queue, signals):
        queue.send(signals)

    def _worker(self):
        # create a callback to be invoked from within ioloop where
        # zmq tasks are to be executed
        PeriodicCallback(self._execute_tasks, 10, io_loop=self._ioloop).start()
        self.logger.debug("Tasks execution started")
        self._ioloop.start()
        self.logger.debug("Tasks execution ended")

    def _execute_tasks(self):
        """ Retrieves and evaluate tasks from within ioloop

        This callback is invoked from ioloop and will continue to execute
        queue tasks until queue is empty
        """
        tasks_pending = True
        while tasks_pending:
            try:
                item = self._tasks_queue.get(block=False)
                try:
                    self._execute(item)
                except:
                    self.logger.exception("Executing: {}".format(item))
                self._tasks_queue.task_done()
            except Empty:
                tasks_pending = False

    def _execute(self, item):
        self.logger.debug("Executing {}".format(item))
        item.target(*item.args, **item.kwargs)
