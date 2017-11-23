"""Paraver related trace generation.

All the Paraver-files (.prv) generation is done through decorators and
mechanisms defined in this module. There are also capabilities for merge and
checks on the generated prv files.

Additionally, this module defines an application capable of performing several
Paraver-related routines, like "merge".
"""

from Queue import Queue
from functools import wraps
import logging
import thread
from threading import Semaphore
import time

from . import prv_traces


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

QUEUE_MAXSIZE = 1000

# Used by pyextrae (COMPSs integration)
TASK_EVENTS = 8000010
PROCESS_CREATION = 100

# Explicit and manually crafted list (there may be functions which are not here)
FUNCS_WITH_PARAVER_DECORATORS = [
    # managers.management
    "prepare_stubs",
    "load_babel_data",
    "deploy_stubs",
    "track_local_available_classes",

    # All the client methods
    "get_account_id",
    "perform_set_of_new_accounts",
    "perform_set_of_operations",
    "new_class_id",
    "new_class",
    "get_domain_id",
    "get_class_info",
    "get_classname_and_namespace_for_ds",
    "get_object_info",
    "get_object_id_from_alias",
    "get_dataset_id",
    "get_object_dataset_id",
    "get_execution_environments_info",
    "get_execution_environment_by_oid",
    "get_storage_location_id_for_ds",
    "get_storage_location_for_ds",
    "get_contract_id_of_dataclay_provider",
    "get_babel_stubs",
    "get_stubs",
    "make_persistent",
    "store_objects",
    "upsert_objects",
    "new_session",
    "execute_implementation",
    "ds_execute_implementation",
    "ds_new_persistent_instance",
    "ds_get_objects",
    "ds_update_objects",
    "get_info_of_session_for_ds",
    "register_object_for_ds",
    "get_object_metadatainfo_for_ds",
    "autoregister_dataservice",

    # api init & finish
    "init",
    "finish",

    # Storage API calls
    "getByID",
    "initWorker",
    "finishWorker",
]

PARAVER_FUNC_MAP = {name: i for i, name in enumerate(FUNCS_WITH_PARAVER_DECORATORS, 500)}


class PrvManager(object):
    """A Paraver Manager is associated to a single output .prv file.

    A single PrvManager should be instantiated for each process. Keep that in
    mind when using multiprocessing features.

    When the instance has already been instantiated, the classmethod get_manager
    returns the instance.
    """
    prv_instance = None

    def __new__(cls, *args):
        """Initialize the static value of prv_instance with the new instance.

        Caution! This constructor will statically overwrite a prior instance of
        PrvManager. It is ok for subprocesses to instantiate their own manager,
        but only with different PID (see also __init__).
        """
        ret = super(PrvManager, cls).__new__(cls, *args)
        cls.prv_instance = ret
        return ret

    def __init__(self, output_name):
        """Initialize the internal Queue and Mutex, and output the synchronization line.

        :param output_base_name: The file path base for the trace output. The
        initialization will add -<pid>.prv to it.

        Caution! Never instantiate a PrvManager more than once in the same
        subprocess --it will silently overwrite the output file.
        """
        self.mutex_queue = Semaphore()
        self.tracing_queue = Queue(QUEUE_MAXSIZE)
        self.output_name = output_name
        with open(self.output_name, 'w') as f:
            f.write("5:{:d}:{:d}\n".format(int(time.time() * 1000),
                                           int(time.clock() * 1000000)))

    @classmethod
    def get_manager(cls):
        """Get the interpreter-wide manager.
        :rtype : PrvManager
        :return: The PrvManager instance to be used.
        """
        return cls.prv_instance

    def close(self):
        """Flush the tracing queue and close everything."""
        logger.debug("Closing PrvManager with output_name: %s", self.output_name)
        with self.mutex_queue:
            if not self.tracing_queue.empty():
                self._dump()

    def _dump(self):
        with open(self.output_name, 'a') as f:
            f.write(self.format_line((0, thread.get_ident(),
                                     int(time.clock() * 1000000),
                                     "1:py.PrvManager.DUMP")))

            while not self.tracing_queue.empty():
                f.write(self.format_line(self.tracing_queue.get_nowait()))

            f.write(self.format_line((0, thread.get_ident(),
                                     int(time.clock() * 1000000),
                                     "0:py.PrvManager.DUMP")))

    def _add_trace(self, prv_id, time_ns, extra):
        """Add an entry to the internal trace Queue, and dump if needed.

        See documentation of Paraver files for more information.
        """
        with self.mutex_queue:
            if self.tracing_queue.full():
                logger.debug("Queue full, dumping to %s", self.output_name)
                self._dump()

            self.tracing_queue.put((prv_id, thread.get_ident(), time_ns, extra), block=False)

    def add_function_trace(self, enter, full_name, prv_value):
        """Trace entry: Function (enter or exit).

        :param enter: Boolean to signal whether it is entering or exiting the method.
        :param full_name: Hierarchical name of the function.
        :param prv_value: Numerical identifier for PyCOMPSs-compliant Paraver tracing.
        """
        try:
            from pyextrae.common import extrae
            if enter:
                extrae.event(TASK_EVENTS, 0)
                extrae.event(TASK_EVENTS, prv_value)
            else:
                extrae.event(TASK_EVENTS, 0)

        except ImportError:
            pass

        self._add_trace(prv_traces.TraceType.METHOD.value, int(time.clock() * 1000000),
                        "{:d}:{}".format(1 if enter else 0, full_name))

    def add_network_send(self, network_type, send_port, request_id, dest_host_ip, message_size, method_id):
        """Trace a certain network send (can be a SEND_REQUEST or a SEND_RESPONSE)."""
        if not _is_network_tracing_enabled():
            return
        self._add_trace(network_type.value, int(time.clock() * 1000000),
                        "{:d}:{:d}:{}:{:d}:{:d}".format(
                            send_port, request_id, dest_host_ip, message_size, method_id))

    def add_network_receive(self, origin_host_ip, origin_host_port, request_id, method_id):
        """Trace a certain network receive (a RESPONSE)."""
        if not _is_network_tracing_enabled():
            return
        self._add_trace(prv_traces.TraceType.RECEIVE.value, int(time.clock() * 1000000),
                        "{}:{:d}:{:d}:{:d}".format(
                            origin_host_ip, origin_host_port, request_id, method_id))

    @classmethod
    def format_line(cls, tuple_info):
        """Return the formatted string from a certain tracing information.

        :param tuple_info: A tuple containing required values for paraver tracing entry
        (three numbers and a string)
        :return: The formatted string
        """
        return "{:d}:{:d}:{:d}:{}\n".format(*tuple_info)


def _is_tracing_enabled(module_name):
    """Check if a certain submodule is to-be-traced.

    :param module_name: The name of the module in which the function/method is.
    :return: True if it should be traced, false otherwise.
    """
    # TODO check something (properties, file, etc.) and return a valid boolean
    # Dummy implementation, always trace
    return True


def _is_network_tracing_enabled():
    """Check if network calls tracing is enabled (globally for all calls).

    :return: True if it should be traced, false otherwise.
    """
    # TODO check something (properties, file, etc.) and return a valid boolean
    # Dummy implementation, always trace
    return True


def trace_method(func):
    """Decorator for class methods that may be traced."""
    if not _is_tracing_enabled(func.__module__):
        return func

    try:
        prv_value = PARAVER_FUNC_MAP[func.func_name]
    except KeyError:
        logger.warning("Method `%s` (in module %s, unknown class) "
                       "is not correctly registered for Paraver",
                       func.func_name, func.__module__)
        prv_value = 999

    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        full_name = "py.{}.{}".format(self.__class__.__name__,
                                      func.func_name)

        prv = PrvManager.get_manager()
        prv.add_function_trace(True, full_name, prv_value)
        # Proceed to the method call
        try:
            ret = func(self, *args, **kwargs)
        finally:
            prv.add_function_trace(False, full_name, prv_value)
        return ret

    return func_wrapper


def trace_function(func):
    """Decorator for functions (not methods) that may be traced."""
    if not _is_tracing_enabled(func.__module__):
        return func

    try:
        prv_value = PARAVER_FUNC_MAP[func.func_name]
    except KeyError:
        logger.warning("Function `%s` (in module %s) is not correctly registered for Paraver",
                       func.func_name, func.__module__)
        prv_value = 999

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        full_name = "py.{}.{}".format(func.__module__, func.func_name)

        prv = PrvManager.get_manager()
        prv.add_function_trace(True, full_name, prv_value)
        # Proceed to the function call
        try:
            ret = func(*args, **kwargs)
        finally:
            prv.add_function_trace(False, full_name, prv_value)
        return ret

    return func_wrapper
