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
"""
This module implements a Dependency Graph that works on top of the ObjDb
object database
"""

from .. import database as onyx_db
from .. import depgraph as onyx_dg

import functools
import collections
import weakref
import copy

__all__ = ["GraphError"]


###############################################################################
class GraphError(Exception):
    pass


###############################################################################
class DependencyGraph(collections.UserDict):
    """
    Class representing the onyx Dependency Graph (a Directed Acyclic Graph).
    Current implementation uses a dictionary that maps (ObjectName, VT, args)
    tuples to graph nodes (instances of GraphNode class).
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        # --- for each object, we keep a mapping of VTs by instance for the VTs
        #     that have been visited while building the graph
        self.vts_by_obj = dict()

    # -------------------------------------------------------------------------
    def clear(self):
        super().clear()
        self.vts_by_obj.clear()

    # -------------------------------------------------------------------------
    def __deepcopy__(self, memo):
        clone = self.__new__(self.__class__)
        clone.data = self.data.copy()
        clone.vts_by_obj = self.vts_by_obj.copy()
        memo[id(self)] = clone
        return clone


###############################################################################
class GraphNode(object):
    """
    Base class representing a node in the Dependency Graph. Implements methods
    to get the node value (using memoization), to invalidate it (when
    recalculation is needed), and to clone the node (for changing its value).
    """
    __slots__ = ("VT", "obj_ref", "parents", "children", "valid", "value")

    # -------------------------------------------------------------------------
    def __init__(self, VT, obj_ref):
        self.VT = VT
        self.obj_ref = obj_ref
        self.parents = set()
        self.children = set()
        self.valid = False
        self.value = None

    # -------------------------------------------------------------------------
    def get_id(self):
        return self.obj_ref().Name, self.VT, ()

    # -------------------------------------------------------------------------
    def get_value(self):
        if self.valid:
            return self.value
        else:
            # --- before calculating the current value of a node we clean-up
            #     the children set: this is needed to make sure that, once the
            #     node is invalidated, we don't keep references to spurious
            #     nodes.
            #     This is achieved by discarding this node from the set of
            #     parents of all its children
            node_id = self.get_id()
            for child in self.children:
                onyx_dg.graph[child].parents.discard(node_id)
            self.children.clear()
            # --- get the ValueType's value from the instance itself and return
            self.value = getattr(self.obj_ref(), self.VT)
            self.valid = True
            return self.value

    # -------------------------------------------------------------------------
    def clone(self):
        cls = self.__class__
        new_node = cls.__new__(cls)
        new_node.VT = self.VT
        new_node.obj_ref = self.obj_ref
        new_node.parents = self.parents.copy()
        new_node.children = self.children.copy()
        new_node.valid = self.valid
        # --- value can be an instance of a mutable class, make a proper copy.
        new_node.value = copy.deepcopy(self.value)
        return new_node

    # -------------------------------------------------------------------------
    def invalidate(self):
        # --- recursively invalidate all parents
        for parent in self.parents:
            onyx_dg.graph[parent].invalidate()

        # --- invalidate this node
        self.valid = False


###############################################################################
class PropertyNode(GraphNode):
    """
    Derived class used Property ValueTypes.
    """
    __slots__ = ()


###############################################################################
class SettableNode(GraphNode):
    """
    Derived class used for nodes whose value can be explicitly set (such as
    StoredAttrs and descriptors that implement a setter).
    """
    __slots__ = ()


###############################################################################
class CallableNode(GraphNode):
    __slots__ = ("args",)

    # -------------------------------------------------------------------------
    def __init__(self, VT, obj_ref, args):
        super().__init__(VT, obj_ref)
        self.args = args

    # -------------------------------------------------------------------------
    def get_id(self):
        return self.obj_ref().Name, self.VT, self.args

    # -------------------------------------------------------------------------
    def get_value(self, *args):
        assert args == self.args
        if self.valid:
            return self.value
        else:
            # --- before calculating the current value of a node we clean-up
            #     the children set: this is needed to make sure that, once the
            #     node is invalidated, we don't keep references to spurious
            #     nodes.
            #     This is achieved by discarding this node from the set of
            #     parents of all its children
            node_id = self.get_id()
            for child in self.children:
                onyx_dg.graph[child].parents.discard(node_id)
            self.children.clear()
            # --- call the object's method with the arguments for this node
            self.value = getattr(self.obj_ref(), self.VT)(*args)
            self.valid = True
            return self.value

    # -------------------------------------------------------------------------
    def clone(self):
        new_node = super().clone()
        # --- shallow copies here should be fine
        new_node.args = self.args[:]
        return new_node


###############################################################################
class PropSubGraphNode(GraphNode):
    __slots__ = ("kwds",)

    # -------------------------------------------------------------------------
    def __init__(self, VT, obj_ref):
        super().__init__(VT, obj_ref)
        self.kwds = {}

    # -------------------------------------------------------------------------
    def get_value(self, **kwds):
        # --- if args and kwds don't match stored values, the graph node is
        #     assumed no longer valid
        if kwds != self.kwds:
            self.valid = False
            self.kwds = kwds

        if self.valid:
            return self.value
        else:
            # --- before calculating the current value of a node we clean-up
            #     the children set: this is needed to make sure that, once the
            #     node is invalidated, we don't keep references to spurious
            #     nodes.
            #     This is achieved by discarding this node from the set of
            #     parents of all its children
            node_id = self.get_id()
            for child in self.children:
                onyx_dg.graph[child].parents.discard(node_id)
            self.children.clear()
            # --- call the object's method with provided arguments
            self.value = getattr(self.obj_ref(), self.VT)(**kwds)
            self.valid = True
            return self.value

    # -------------------------------------------------------------------------
    def clone(self):
        new_node = super().clone()
        # --- shallow copies here should be fine
        new_node.kwds = self.kwds.copy()
        return new_node


###############################################################################
class BaseVT(object):
    pass


###############################################################################
class PropertyVT(BaseVT):
    def __init__(self, fget):
        # --- ensure that the decorated method has the following signature:
        #         f(self, graph)
        #
        if fget.__code__.co_argcount == 2:
            self.fget = fget
        elif fget.__code__.co_argcount < 2:
            raise GraphError("Missing self and/or "
                             "graph in the method definition")
        elif fget.__code__.co_argcount > 2:
            raise GraphError("A Property VT cannot accept "
                             "extra arguments besides self and graph")

    def __get__(self, instance, cls=None):
        if instance is None:
            # --- it's convenient to return the descriptor itself when accessed
            #     on the class so that getattr(type(obj)), "vt") works fine
            return self

        caller = (instance.Name, self.fget.__name__, ())
        return self.fget(instance, functools.partial(get_node_val, caller))

    def __set__(self, instance, value):
        raise AttributeError("Cannot set a Property VT")

    def node(self, VT, ref, args):
        return PropertyNode(VT, ref)


###############################################################################
class SettableVT(BaseVT):
    def __init__(self, fget, fset, name):
        self.__name__ = name
        # ---ensure that getter and setter functions have the following
        #     signature:
        #         fget(self, graph), fset(self, graph, value)
        #
        if fget.__code__.co_argcount == 2:
            self.fget = fget
        elif fget.__code__.co_argcount < 2:
            raise GraphError("Missing self and/or "
                             "graph in the getter definition")
        elif fget.__code__.co_argcount > 2:
            raise GraphError("A Settable VT getter cannot accept "
                             "extra arguments besides self and graph")
        if fset.__code__.co_argcount == 3:
            self.fset = fset
        elif fset.__code__.co_argcount < 3:
            raise GraphError("Missing self and/or graph "
                             "and/or value in the setter definition")
        elif fset.__code__.co_argcount > 3:
            raise GraphError("A Settable VT setter cannot accept "
                             "extra arguments besides self, graph, and value")

    def __get__(self, instance, cls=None):
        if instance is None:
            # --- it's convenient to return the descriptor itself when accessed
            #     on the class so that getattr(type(obj)), "vt") works fine
            return self
        caller = (instance.Name, self.__name__, ())
        return self.fget(instance, functools.partial(get_node_val, caller))

    def __set__(self, instance, value):
        caller = (instance.Name, self.__name__, ())
        self.fset(instance, functools.partial(get_node_val, caller), value)

    def node(self, VT, ref, args):
        return SettableNode(VT, ref)


###############################################################################
class CallableVT(BaseVT):
    """
    Description:
        Descriptor used for callable ValueTypes (methods with input arguments).
        Notice that for a callable ValueType the input arguments are part of
        the node_id so that the same ValueType called with different arguments
        will produce different nodes in the graph.
        The limitation is that only positional arguments are supported.
    Signature, example:
        func(self, graph, x, y, z=1, ...)
    """
    def __init__(self, func):
        if func.__code__.co_argcount < 3:
            raise GraphError("CallableVT signature requires a "
                             "minimum of one argument besides self and graph")
        self.func = func

    def __get__(self, instance, cls=None):
        self.instance = instance
        return self

    def __set__(self, instance, value):
        raise AttributeError("Cannot set a CalcPositional VT")

    def __call__(self, *args):
        caller = (self.instance.Name, self.func.__name__, args)
        return self.func(self.instance,
                         functools.partial(get_node_val, caller), *args)

    def node(self, VT, ref, args):
        return CallableNode(VT, ref, args)


###############################################################################
class PropSubGraphVT(BaseVT):
    """
    Description:
        Descriptor used to represent a subgraph with property-like nodes.
        The input arguments are treated as children of the node so that when
        called with different arguments the node in the graph will always be
        invalidated.
        The limitation is that only keyword arguments are supported.
    Signature, example:
        func(self, graph, x=1, y=None, ...)
    """
    def __init__(self, func):
        argcount = func.__code__.co_argcount
        if argcount < 3:
            raise GraphError("PropSubGraphVT signature requires a "
                             "minimum of one argument besides self and graph")
        if not func.__defaults__ or  (argcount - 2 != len(func.__defaults__)):
            raise GraphError("PropSubGraphVT signature "
                             "requires all arguments besides self "
                             "and graph to provide a default value")
        self.func = func

    def __get__(self, instance, cls=None):
        self.instance = instance
        return self

    def __set__(self, instance, value):
        raise AttributeError("Cannot set a CalcKeywords VT")

    def __call__(self, **kwds):
        caller = (self.instance.Name, self.func.__name__, ())
        graph = functools.partial(get_node_val, caller)
        return self.func(self.instance, graph, **kwds)

    def node(self, VT, ref, args):
        return PropSubGraphNode(VT, ref)


# -----------------------------------------------------------------------------
def create_node(node_id):
    """
    Description:
        Helper function used to create a new node.
    Inputs:
        node_id - the (Name, VT, args) tuple
    Returns:
        A subclass of GraphNode.
    """
    if len(node_id) == 2:
        obj_name, VT = node_id
        args = ()
    else:
        obj_name, VT, args = node_id

    # --- the instance of the graph keeps a map of VTs by object
    try:
        onyx_dg.graph.vts_by_obj[obj_name].add((VT, args))
    except KeyError:
        onyx_dg.graph.vts_by_obj[obj_name] = {(VT, args)}

    obj = onyx_db.obj_clt.get(obj_name)

    if VT == "StoredAttrs":
        # --- StoredAttrs is special insofar that we don't want it to be
        #     settable/changeable
        return GraphNode(VT, weakref.ref(obj))
    elif VT in obj.StoredAttrs:
        # --- all stored attributes as well as StoredAttrs itself are settable
        #     by definition
        return SettableNode(VT, weakref.ref(obj))
    else:
        # --- use the node constructor of the ValueType descriptor itself
        return getattr(obj.__class__, VT).node(VT, weakref.ref(obj), args)


# -----------------------------------------------------------------------------
def get_node_val(caller, obj, VT, *args, **kwds):
    """
    Description:
        This is the proper way of calling a VT on-graph. Use this function to
        get a value type from within a method that has been decorated by
        @ValueType().
    Inputs:
        caller - caller node identity
        obj    - target object as defined in database (or memory)
        VT     - target value type (a stored attribute or a method of an ufo
                 class decorated by @ValueType())
        *args  - positional arguments used to call the target method
        **kwds -      named arguments used to call the target method
    Returns:
        The VT value.
    """
    # --- get the calling node from the graph (the node is created if it
    #     doesn't exsist)
    try:
        caller_node = onyx_dg.graph[caller]
    except KeyError:
        onyx_dg.graph[caller] = caller_node = create_node(caller)

    # --- define target id tuple
    if isinstance(obj, str):
        target = (obj, VT, args)
    else:
        target = (obj.Name, VT, args)

    # --- get the target node from the graph (the node is created if it
    #     doesn't exsist)
    #     NB: this raises the following exceptions BEFORE changing the state
    #         of the graph:
    #         - ObjNotFound    if obj is not found in database or memory
    #         - AttributeError if obj doesn't have a VT attribute
    try:
        target_node = onyx_dg.graph[target]
    except KeyError:
        onyx_dg.graph[target] = target_node = create_node(target)

    caller_node.children.add(target)
    target_node.parents.add(caller)

    # --- now that the graph is set up, return target node value. we make a
    #     deepcopy to make sure we never return a reference to a mutable value
    return copy.deepcopy(target_node.get_value(*args, **kwds))
