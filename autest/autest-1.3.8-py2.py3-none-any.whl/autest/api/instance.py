from __future__ import absolute_import, division, print_function
import types

import hosts.output as host


def AddMethodToInstance(obj, method, name=None):
    '''Add method to provided object instance with optional name'''
    if name is None:
        name = method.__name__
    setattr(obj, name, types.MethodType(method, obj))
    host.WriteVerbose("api",
                      'Added method "{0}" to instance {1}'.format(name, obj))
