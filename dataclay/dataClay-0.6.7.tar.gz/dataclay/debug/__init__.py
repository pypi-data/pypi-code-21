"""Hacks, utilities and shortcuts to debugging stuff.

This module can be used for debugging the dataClay application. It is intended
to be used for internal development, not final product features.

The final package will not include this package. However, tests and unittests
may (should, are encouraged to) use features provided here.
"""

from dataclay.managers.classes.properties import DCLAY_PROPERTY_PREFIX

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

TIMEOUT = 300


def get_property(obj, prop_name):
    """Force a non-remote get of a property.
    :param obj: dataClay object (from a stub).
    :param prop_name: Name of the property (non-mangled).
    :return: The local (probably invalid for persistent objects) of the
    class' property.
    """
    return getattr(obj, DCLAY_PROPERTY_PREFIX + prop_name)


def set_property(obj, prop_name, value):
    """Force a non-remote set of a property.
    :param obj: dataClay object (from a stub).
    :param prop_name: Name of the property (non-mangled).
    :param value: Value that will be assigned to the property.

    Note that this is probably an invalid operation for persistent objects.
    Even for persistent objects, this operation is done locally.
    """
    setattr(obj, DCLAY_PROPERTY_PREFIX + prop_name, value)
