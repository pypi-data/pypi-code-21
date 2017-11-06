###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from .graph_api import ValueType

import types

__all__ = [
    "RetainedFactory",
    "InheritAsProperty",
    "DiscardInheritedAttribute",
]


###############################################################################
class RetainedFactory(object):
    """
    Description:
        ValueType factory that implements a descriptor protocol used to
        represent pseudo-attribute VTs, i.e. VTs that can be set but are not
        persisted in database.
    Inputs:
        default - if None use the VT function to calculate the current value,
                  otherwise use default.

    Typical use cases are:

    1) for the implementation of retained properties (such as Spot) where the
       typical syntax is as follows:

           @RetainedFactory()
           def Spot(self, graph):
               ...

    2) for in the implementation of edit screens where the typical
       syntax is as follows:

            @RetainedFactory(default=...)
            def MyVt(self, graph): pass
    """
    # -------------------------------------------------------------------------
    def __init__(self, default=None):
        self.value = default

    # -------------------------------------------------------------------------
    def __call__(self, func):
        def getter(instance, graph):
            if self.value is None:
                return func(instance, graph)
            else:
                return self.value

        def setter(instance, graph, value):
            self.value = value

        # --- return a settable descriptor ValueType
        return ValueType("Settable", getter, setter)(func)


###############################################################################
class InheritAsProperty(object):
    """
    Description:
        Class decorator used to replace one or more stored attributes of the
        super class with properties pointing to the same attribute of another
        object.
    Inputs:
        attrs      - a list of stored attributes of the super-class that are
                     to be replaced by Property value types.
        value_type - a pointer to the instance of the ufo class from which we
                     are inheriting stored attributes as properties.
                     Each stored attribute in attrs will be replaced with by
                     property VT.
    """
    template = ("def template(self, graph):\n"
                "    return graph(graph(self, '{0:s}'), '{1:s}')")

    # -------------------------------------------------------------------------
    def __init__(self, attrs, value_type):
        self.attrs = attrs
        self.value_type = value_type

    # -------------------------------------------------------------------------
    def __call__(self, cls):
        for attr in self.attrs:
            # --- discard from set of StoredAttrs attributes (discard does
            #     nothing if cls doesn't have such attribute)
            cls._json_fields.discard(attr)
            cls.StoredAttrs.discard(attr)

            # --- create Property-ValueType
            mod = types.ModuleType("__templates")
            exec(self.template.format(self.value_type, attr), mod.__dict__)
            func = types.FunctionType(mod.template.__code__, {}, name=attr)
            setattr(cls, attr, ValueType()(func))

        return cls


###############################################################################
class DiscardInheritedAttribute(object):
    """
    Description:
        Class decorator used to dis-inherit one or more stored attributes of
        the super class, ususally so that they can be re-implemented as
        properties.
    Inputs:
        attrs - a list of stored attributes of the super-class that are
                to be discarded.
    """
    # -------------------------------------------------------------------------
    def __init__(self, attrs):
        self.attrs = attrs

    # -------------------------------------------------------------------------
    def __call__(self, cls):
        for attr in self.attrs:
            # --- discard from set of StoredAttrs attributes (discard does
            #     nothing if cls doesn't have such attribute)
            cls._json_fields.discard(attr)
            cls.StoredAttrs.discard(attr)

        return cls
