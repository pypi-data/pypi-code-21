import os
import uuid
from distutils.util import strtobool

import dataclay.api
from dataclay import runtime

from dataclay.core.paraver import trace_function
# "Publish" the StorageObject (which is a plain DataClayObject internally)
from dataclay.managers.classes import DataClayObject as StorageObject
# Also "publish" the split method
from dataclay.contrib.splitting import split

_initialized = False

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


@trace_function
def getByID(object_id):
    """Get a Persistent Object from its OID.
    :param object_id: The OID (UUID of the object)
    :return: The (Persistent) DataClayObject
    """
    return runtime.get_object_by_id(uuid.UUID(object_id))


@trace_function
def initWorker(config_file_path, **kwargs):
    """Worker-side initialization.

    :param config_file_path: Path to storage.properties configuration file.
    :param kwargs: Additional arguments, currently unused. For future use
    and/or other Persistent Object Library requirements.
    """
    dataclay.api.init(config_file_path)


def initWorkerPostFork():
    dataclay.api.reinitialize_clients()


def init(config_file_path, **kwargs):
    """Master-side initialization.

    Identical to initWorker (right now, may change).
    """
    dataclay.api.init(config_file_path)


@trace_function
def finishWorker(**kwargs):
    """Worker-side finalization.

    :param kwargs: Additional arguments, currently unused. For future use
    and/or other Persistent Object Library requirements.
    """
    dataclay.api.finish()


def finish(**kwargs):
    """Master-side initialization.

    Identical to finishworker (right now, may change).
    """
    dataclay.api.finish()


class TaskContext(object):
    def __init__(self, logger, values, config_file_path=None, **kwargs):
        """Initialize the TaskContext for the current task.
        :param logger: A logger that can be used for the storage.api
        :param values: The values of the Task (unused right now)
        :param config_file_path: DEPRECATED. Was required by dataClay.
        Has been moved to initWorker.
        :param kwargs: Additional arguments, currently unused. For future use
        and/or other Persistent Object Library requirements.

        A task is about to be executed and this ContextManager encloses its
        execution. This context is used by the COMPSs Worker.
        """
        self.logger = logger
        self.values = values

    def __enter__(self):
        """Perform initialization (ContextManager starts)"""
        self.logger.info("Starting task")

    def __exit__(self, type, value, tb):
        """Perform finalization (ContextManager ends)"""
        # ... manage exception if desired
        if type is not None:
            self.logger.warn("Exception received: %s", type)
            pass  # Exception occurred
            # Return true if you want to suppress the exception

        # Finished
        self.logger.info("Ending task")


if strtobool(os.getenv("DEACTIVATE_STORAGE_LIBRARY", "False")):
    from dataclay.contrib.dataclay_dummy import deactivate_storage_library
    deactivate_storage_library()

    # Note that dataclay.StorageObject, at this moment should already be "deactivated"
    # (i.e., it should be a dummy no-op class)
    StorageObject = dataclay.StorageObject
