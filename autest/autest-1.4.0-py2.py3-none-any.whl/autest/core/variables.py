from __future__ import absolute_import, division, print_function
from autest.common.constructor import call_base, smart_init
import autest.common.is_a as is_a

# object inherits dict type


@smart_init
class Variables(dict, object):
    @call_base(dict=(), object=())
    def __init__(self, val=None, parent=None):
        self.__parent = parent
        if val is None:
            val = {}
        if not is_a.Dict(val):
            raise TypeError("value needs to be a dict type")
        self.update(val)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            if self.__parent:
                return self.__parent[name]
            else:
                raise AttributeError("%r has no attribute %r" %
                                     (self.__class__, name))

    def __setattr__(self, name, value):
        self[name] = value
