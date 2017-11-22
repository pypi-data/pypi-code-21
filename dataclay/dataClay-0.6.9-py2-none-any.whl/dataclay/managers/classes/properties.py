import logging
from collections import namedtuple

from dataclay import runtime

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

DCLAY_PROPERTY_PREFIX = "_dataclay_property_"
DCLAY_GETTER_PREFIX = "$$get"
DCLAY_SETTER_PREFIX = "$$set"

PreprocessedProperty = namedtuple('PreprocessedProperty', field_names=[
    'name', 'position', 'type', 'beforeUpdate', 'afterUpdate'])


class DynamicProperty(property):
    """DataClay implementation of the `property` Python mechanism.

    This class is similar to property but is not expected to be used with
    decorators. Instead, the initialization is done from the ExecutionGateway
    metaclass, containing the required information about the property
    """
    __slots__ = ("p_name",)

    def __init__(self, property_name):
        """Initialize the DynamicProperty with the name of its property.

        Not calling super deliberately.

        The semantics and behaviour changes quite a bit from the property
        built-in, here we only store internally the name of the property and
        use dataClay friendly setters and getters.
        """
        self.p_name = property_name

    def __get__(self, obj, type_=None):
        """Getter for the dataClay property

        If the object is loaded, perform the getter to the local instance (this
        is the scenario for local instances and Execution Environment fully
        loaded instances).

        If the object is not loaded, perform a remote execution (this is the
        scenario for client remote instances and also Execution Environment
        non-loaded instances, which may either "not-yet-loaded" or remote)
        """
        logger.debug("Calling getter for property %s", self.p_name)

        if obj._dclay_instance_extradata.loaded_flag:
            # This bypasses all the metaclass mechanisms
            # (no need for an infinite circular reference)
            return object.__getattribute__(obj, "%s%s" % (DCLAY_PROPERTY_PREFIX, self.p_name))
        else:
            return runtime.execute_implementation_aux(DCLAY_GETTER_PREFIX + self.p_name, obj, ())

    def __set__(self, obj, value):
        """Setter for the dataClay property

        See the __get__ method for the basic behavioural explanation.
        """
        logger.debug("Calling setter for property %s", self.p_name)

        if obj._dclay_instance_extradata.loaded_flag or not obj.is_persistent():
            # This bypasses all the metaclass mechanisms
            # (no need for an infinite circular reference)
            object.__setattr__(obj, "%s%s" % (DCLAY_PROPERTY_PREFIX, self.p_name), value)
        else:
            runtime.execute_implementation_aux(DCLAY_SETTER_PREFIX + self.p_name, obj, (value,))
            # Ignore return

class ReplicatedDynamicProperty(DynamicProperty):
    beforeUpdate = None
    afterUpdate = None

    def __init__(self, property_name, before_method, after_method):
        super(ReplicatedDynamicProperty, self).__init__(property_name)
        self.beforeUpdate = before_method
        self.afterUpdate = after_method

    def __set__(self, obj, value):
        """Setter for the dataClay property

        See the __get__ method for the basic behavioural explanation.
        """
        logger.debug("Calling setter for property %s", self.p_name)

        if obj._dclay_instance_extradata.loaded_flag or not obj.isPersistent():
            object.__setattr__(obj, "%s%s" % (DCLAY_PROPERTY_PREFIX, self.p_name), value)
        else:
            if self.beforeUpdate is not None:
                runtime.execute_implementation_aux(self.beforeUpdate, obj, (DCLAY_SETTER_PREFIX + self.p_name, value))
            runtime.execute_implementation_aux(DCLAY_SETTER_PREFIX + self.p_name, obj, (value,))
            if self.afterUpdate is not None:
                runtime.execute_implementation_aux(self.afterUpdate, obj, (DCLAY_SETTER_PREFIX + self.p_name, value))
