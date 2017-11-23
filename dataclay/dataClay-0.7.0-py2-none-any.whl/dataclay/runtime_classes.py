from decorator import decorator
from enum import Enum
import logging
from weakref import WeakValueDictionary


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


@decorator
def proxified_runtime_method(f, self, *args, **kwargs):
    try:
        func = self._methods[f.__name__]
    except KeyError:
        if self._rt_type is None:
            raise RuntimeError("The dataclay.runtime module has not been populated yet.")
        else:
            raise RuntimeError("The Runtime function %s is not available in this environment."
                               % f.__name__)
    except TypeError:
        raise RuntimeWarning(
            "The Runtime has been tear-down. No methods available "
            "(in particular, no %s available)" % f.__name__
        )

    return func(self, *args, **kwargs)


class RuntimeType(Enum):
    """Running modes of Python source in dataClay.

    Currently there exist the following modes:
      - [client] For client-side execution --outside dataClay.
      - [manage] The management mode for initialization/bootstraping the client.
      - [exe_env] Execution Environment mode (inside dataClay infrastructure).
    """
    client = 1
    manage = 2
    exe_env = 3


class ProxyRuntime(object):
    """Proxy Class for divergent behaviour between DataService and client.

    This class manages all the runtime-specific behaviour. The behaviour will
    change between the Execution Environment and the client. The initialization
    of each of them is expected to call the establish method in order to set
    all the methods and the Runtime Type.

    This is specially useful in serialization-related functions, which are
    very similar between the client and the server, but with notable exceptions.
    Those notable exceptions are in this module, and the client should
    dynamically override those when importing dataclay.api. The same applies to
    the server, which should do something similar during initialization.
    """

    def __init__(self):
        """Initialize the proxy, without any execution information."""
        self._rt_type = None
        self._methods = dict()

        # All in-memory objects (which may be loaded or not yet), indexed by ObjectID
        self.inmemory_objects = WeakValueDictionary()

        # Track the opened connection by {ExecutionEnvironment|StorageLocation}ID
        # Special cases:
        #   - @LM connection to the LogicModule (both used by client and server)
        #   - @STORAGE connection to the "local" Storage Location (used by the
        #     Execution Environment).
        # Additionally, the Execution Environment may save connections to the different
        # DataServices when required.
        self.ready_clients = dict()

    def establish(self, rt_type, methods, attributes=None):
        """Establish the Runtime for the instance.

        :param RuntimeType rt_type: The Runtime Type for the instance.
        :param dict methods: A dictionary of methods for the runtime.
        :param dict attributes: Extra attributes for the instance.
        :rtype None:

        Note that the attributes will be updated into the internal __dict__, so
        take extra care when defining the keys.
        """
        if self._rt_type is not None:
            logger.error("RunTime Type should be assigned once per run.")
            # Log the error but do not raise

        self._rt_type = rt_type

        self._methods = methods
        if attributes is not None:
            self.__dict__.update(attributes)

    def teardown(self):
        """Clean up the runtime, avoiding any further call to it.

        This teardown is typically used in a `atexit` registered function or
        method. The purpose is avoiding further calls once the clean up has
        started. This means that the clean up should ensure to fulfill the
        work that requires to be done --like storing the persistent objects.

        The caller has the responsibility of retrieving important parameters
        (like inmemory_objects and ready_clients) as required. After teardown
        execution, the caller shall not use any other methods of the runtime.

        This method is idempotent.
        """
        self._rt_type = None
        self._methods = None
        self.inmemory_objects = None
        self.ready_clients = None

    @property
    def current_type(self):
        """Get the global RuntimeType, assuming it has been previously been set."""
        if self._rt_type is None:
            logger.error("RunTime Type has not been set.")
            # Log the error but do not raise

        return self._rt_type

    @proxified_runtime_method
    def get_object_by_id(self, object_id):
        """Given a certain ObjectID, return the (persistent) object.

        :param uuid.UUID object_id: The ObjectID for the Persistent Object.
        :rtype: dataclay.DataClayObject
        :return: An DataClayObject instance.
        """
        pass

    @proxified_runtime_method
    def get_execution_environment_by_oid(self, object_id):
        """Given a certain ObjectID, return a single (random-ish) Execution Environment.

        :param uuid.UUID object_id: The ObjectID for the Persistent Object.
        :return: A valid ExecutionEnvironment for the given object.
        """
        pass

    @proxified_runtime_method
    def get_all_execution_environments_by_oid(self, object_id):
        """Given a certain ObjectID, return all its Execution Environments.
        :param uuid.UUID object_id: The ObjectID for the Persistent Object.
        :return: All the ExecutionEnvironment for the given object.
        """
        pass

    @proxified_runtime_method
    def make_persistent(self, instance, alias, backend_id, recursive):
        """Given a local DataClayObject instance, make it persistent.

        :param dataclay.DataClayObject instance: The instance to be made persistent.
        :param str | None alias: Desired alias for the object.
        :param uuid.UUID | None backend: Optional destination.
        :param boolean | True recursive: Recursive make persistent
        :rtype None:
        """
        pass

    @proxified_runtime_method
    def move_object(self, instance, dest_stloc_id):
        """Move a DataClayObject instance to a certain destination.

        :param dataclay.DataClayObject instance: The instance that is gonna be moved.
        :param uuid.UUID dest_stloc_id: Destination StorageLocationID.
        :rtype None:
        """
        pass

    @proxified_runtime_method
    def get_by_alias(self, dclay_cls, alias):
        """Given a DataClayObject class, get an instance given its alias.

        :param dclay_cls: The class (derived from DataClayObject).
        :param str alias: The alias of the stored object.
        :rtype dataclay.DataClayObject instance:
        :return: A DataClayObject instance.
        """
        pass

    @proxified_runtime_method
    def delete_alias(self, dclay_cls, alias):
        """Removes the alias of an object.

        :param dclay_cls: The class (derived from DataClayObject).
        :param str alias: The alias of the stored object.
        """
        pass

    @proxified_runtime_method
    def get_execution_environments_info(self):
        """Get the information of all the available backends.

        :rtype dict:
        :return: A dictionary, indexed by ExecutionEnvironmentID, of ExecutionEnvironment
        structures.
        """
        pass

    @proxified_runtime_method
    def store_object(self, instance):
        """Store a object to the Storage Location.

        :param dataclay.DataClayObject instance: The instance to be stored.
        :return None:

        Note that this can only used in the ExecutionEnvironment side, not by
        the client.
        """
        pass

    @proxified_runtime_method
    def new_instance(self, class_id, **kwargs):
        """Get a new object instance for a given MetaClassID.

        :param uuid.UUID class_id: The UUID for the MetaClassID.
        :param kwargs: The extra parameters that will be used for the
        _dclay_instance_extradata field.
        :rtype: dataclay.DataClayObject
        :return: Empty instance, with extradata initialized.
        """
        pass

    @proxified_runtime_method
    def execute_implementation_aux(self, operation_name, instance, parameters):
        """Auxiliar method for execute_implementation behaviour.

        :param str operation_name: Name of the method which will be executed.
        :param dataclay.DataClayObject instance: Persistent Object instance to
        be used for execution.
        :param list | tuple parameters: Parameters (positional arguments) for the
        implementation call.
        :return: The result of the execution.

        This method is mainly used by the instrumented methods and properties
        of DataClayObject (see also ExecutionGateway).
        """
        pass

    @proxified_runtime_method
    def new_persistent_instance_aux(self, klass, args, kwargs):
        """Auxiliar method for new_persistent_instance behaviour.

        :param klass: The dataClay class.
        :param args: Arguments for the __init__ method.
        :param kwargs: Keyword arguments for the __init__ method.
        :return: A new *proxy* instance for the given class.
        """
        pass
