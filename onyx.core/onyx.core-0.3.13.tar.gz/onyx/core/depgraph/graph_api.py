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

from ..database.ufo_base import get_base_classes
from ..database.objdb import ObjNotFound
from ..database.objdb_api import DelObj
from .graph import DependencyGraph, SettableNode, CallableNode, create_node
from .graph import BaseVT, PropertyVT, SettableVT, CallableVT, PropSubGraphVT
from .graph import GraphError

from .. import database as onyx_db
from .. import depgraph as onyx_dg

import copy

__all__ = [
    "UseGraph",
    "ValueType",
    "CreateInMemory",
    "RemoveFromGraph",
    "PurgeObj",
    "GetNode",
    "GetVal",
    "SetVal",
    "InvalidateNode",
    "NodesByObjName",
    "ValueTypesByInstance",
    "IsInstance",
    "ChildrenSet",
    "LeafNodes",
    "SettableNodes",
]


###############################################################################
class UseGraph(object):
    """
    Context manager used to activate the dependency graph.
    """
    def __init__(self, graph=None):
        self.graph = graph or DependencyGraph()
        self.previous = None

    def __enter__(self):
        # --- make sure the global database client is available
        if onyx_db.obj_clt is None:
            raise GraphError("global database client is not "
                             "available (did you call UseDatabase?)")

        # --- swap the graph instances
        self.previous = onyx_dg.graph
        onyx_dg.graph = self.graph

    def __exit__(self, *args, **kwds):
        onyx_dg.graph = self.previous
        # --- returns False so that all execptions raised will be propagated
        return False


###############################################################################
class ValueType(object):
    """
    This decorator trasforms methods of classes derived from UfoBase into a
    ValueType descriptor.
    """
    # -------------------------------------------------------------------------
    def __init__(self, vt_type="Property", fget=None, fset=None):
        self.vt_type = vt_type
        if vt_type == "Settable":
            if fget is None or fset is None:
                raise GraphError("Settable VT needs both getter and setter")
            else:
                self.fget = fget
                self.fset = fset

    # -------------------------------------------------------------------------
    def __call__(self, func):
        if self.vt_type == "Property":
            return PropertyVT(func)
        elif self.vt_type == "Settable":
            return SettableVT(self.fget, self.fset, func.__name__)
        elif self.vt_type == "Callable":
            return CallableVT(func)
        elif self.vt_type == "PropSubGraph":
            return PropSubGraphVT(func)
        else:
            raise GraphError("Unrecognized VT type {0:s}".format(self.vt_type))


# -----------------------------------------------------------------------------
def CreateInMemory(instance):
    """
    Description:
        Helper function that adds an instance of an object derived from
        UfoBase in memory so that  all its VTs are on-graph and their values
        can be retrieved using the standard API (GetVal or graph when from
        within a mothod decorated by ValueType).
    Inputs:
        instance - the instance of an object derived from UfoBase
    Returns:
        The instance itself.
    """
    try:
        # --- return a reference to the cached instance with same name
        return onyx_db.obj_instances[instance.Name]
    except KeyError:
        # --- add object instance to global cache
        onyx_db.obj_instances[instance.Name] = instance
        # --- return a reference to the instance
        return instance


# -----------------------------------------------------------------------------
def RemoveFromGraph(obj):
    """
    Description:
        Remove all VTs of an object from the graph.
    Inputs:
        obj - instance (or name) of an object derived from UfoBase
    Returns:
        None.
    """
    name = obj if isinstance(obj, str) else obj.Name

    # --- first invalidate all nodes referring to this object
    for node in NodesByObjName(name):
        node.invalidate()

    # --- then remove from the graph all nodes referring to this object
    for node in NodesByObjName(name):
        del onyx_dg.graph[node.get_id()]

    # --- finally remove the object itself from the VT mapping (if present)
    onyx_dg.graph.vts_by_obj.pop(name, None)


# -----------------------------------------------------------------------------
def PurgeObj(obj):
    """
    Description:
        Remove all VTs of an object from the graph and then delete the object
        from the database.
    Inputs:
        obj - an instance of an object derived from UfoBase (or its name)
    Returns:
        None.
    """
    RemoveFromGraph(obj)
    try:
        DelObj(obj)
    except ObjNotFound:
        pass


# -----------------------------------------------------------------------------
def GetNode(obj, VT, args=()):
    """
    Description:
        Fetches a node from the graph if present, otherwise it creates the new
        node and adds it to the graph.
        NB: application code shouldn't ever need to fetch a node directly, but
            rather use GetVal.
    Inputs:
        obj  - instance (or name) of an object derived from UfoBase
        VT   - name of the target ValueType
        args - tuple of arguments defining a callable node (optional)
    Returns:
        A hard reference to the node in the graph.
    """
    name = obj if isinstance(obj, str) else obj.Name
    node_id = (name, VT, args)

    try:
        return onyx_dg.graph[node_id]
    except KeyError:
        onyx_dg.graph[node_id] = node = create_node(node_id)
        return node


# -----------------------------------------------------------------------------
def GetVal(obj, VT, *args, **kwds):
    """
    Description:
        This is the proper way of calling a VT off-graph. Use this method to
        get a value type from a script.
    Inputs:
        obj    - instance (or name) of an object derived from UfoBase
        VT     - name of the target ValueType
        *args  - positional arguments used to call the target method
        **kwds -      named arguments used to call the target method
    Returns:
        The VT value.
    """
    name = obj if isinstance(obj, str) else obj.Name
    node_id = (name, VT, args)

    try:
        node = onyx_dg.graph[node_id]
    except KeyError:
        onyx_dg.graph[node_id] = node = create_node(node_id)

    # --- return node value. we make a deepcopy to make sure we never return a
    #     reference to a mutable value
    return copy.deepcopy(node.get_value(*args, **kwds))


# -----------------------------------------------------------------------------
def SetVal(obj, VT, value):
    """
    Description:
        Set the value of a stored attribute on-graph (i.e. the new value is
        visible on the graph). When the instance is persisted by calling
        UpdateObj(obj.Name), the new attribute's value is persisted as well.
        NB: only leaf nodes (i.e. nodes that are object's stored attributes)
            can be set.
    Inputs:
        obj   - instance (or name) of an object derived from UfoBase
        VT    - name of the target ValueType
        value - the value to set the VT to
    Returns:
        None.
    """
    name = obj if isinstance(obj, str) else obj.Name

    # --- get the target node from the graph
    node_id = (name, VT, ())

    try:
        node = onyx_dg.graph[node_id]
    except KeyError:
        onyx_dg.graph[node_id] = node = create_node(node_id)

    if not isinstance(node, SettableNode):
        raise GraphError("({0:s},{1:s}) "
                         "is not a settable VT".format(*node_id))

    # --- discard this node from the set of parents of all its children
    for child in node.children:
        onyx_dg.graph[child].parents.discard(node_id)

    # --- remove all its children
    node.children.clear()

    # --- invalidate all its parents
    for parent in node.parents:
        onyx_dg.graph[parent].invalidate()

    # --- set the node value and set its state to valid
    node.value = value
    node.valid = True

    # --- set attribute in the cached instance of the object
    setattr(node.obj_ref(), node.VT, node.value)


# -----------------------------------------------------------------------------
def InvalidateNode(obj, VT, args=()):
    """
    Description:
        Invalidate a node in the graph.
    Inputs:
        obj  - instance (or name) of an object derived from UfoBase
        VT   - name of the target ValueType
        args - tuple of arguments defining a callable node (optional)
    Returns:
        None.
    """
    name = obj if isinstance(obj, str) else obj.Name
    node = GetNode(name, VT, args)
    if isinstance(node, CallableNode) and args == ():
        raise GraphError("To invalidate a clalable node it is "
                         "mandatory to specify the tuple of arguments")
    node.invalidate()


# -----------------------------------------------------------------------------
def NodesByObjName(obj):
    """
    Description:
        Generator: returns all the nodes that reference the same object
    Inputs:
        obj - instance (or name) of an object derived from UfoBase
    Yields:
        Graph nodes.
    """
    name = obj if isinstance(obj, str) else obj.Name
    try:
        for VT, args in onyx_dg.graph.vts_by_obj[name]:
            yield onyx_dg.graph[(name, VT, args)]
    except KeyError:
        raise StopIteration


# -----------------------------------------------------------------------------
def ValueTypesByInstance(obj):
    """
    Description:
        Returns a list of all value types for object obj
    Inputs:
        obj - instance (or name) of an object derived from UfoBase
    Returns:
        A list of VT names.
    """
    if isinstance(obj, str):
        obj = onyx_db.obj_clt.get(obj)

    cls = obj.__class__
    calc = [name for name, VT in
            cls.__dict__.items() if isinstance(VT, BaseVT)]

    return list(obj.StoredAttrs) + calc


# -----------------------------------------------------------------------------
def IsInstance(name, obj_type):
    """
    Description:
        This is the equivalent of isinstance, but takes the instance name and
        the class name as inputs.
    Inputs:
        name     - the instance name
        obj_type - the class name
    """
    obj = onyx_db.obj_clt.get(name)
    bases = set(get_base_classes(obj.__class__))
    return obj_type in bases


# -----------------------------------------------------------------------------
def children_iterator(node_id, child_VT, obj_type):
    for name, vt, args in onyx_dg.graph[node_id].children:
        if vt == child_VT:
            if obj_type is None:
                yield name
            else:
                obj = onyx_db.obj_instances[name]
                bases = set(get_base_classes(obj.__class__))
                if obj_type in bases:
                    yield name
        else:
            for kid in children_iterator((name, vt, args), child_VT, obj_type):
                yield kid


# -----------------------------------------------------------------------------
def ChildrenSet(node_id, child_VT, obj_type=None, graph=None):
    """
    Description:
        Given a node id, return the names of all the objects that, combined
        with a specific VT, are its children.
    Inputs:
        node_id  - parent node_id, in the form (Name, VT, args), where args can
                   be skipped in place of an empty tuple
        child_VT - children ValueType's name
        obj_type - if set, children must be subclass of this class
        graph    - if set, function used to generate graph topology
    Yields:
        A set with object names.
    """
    obj, VT, *args = node_id
    name = obj if isinstance(obj, str) else obj.Name
    node_id = (name, VT, tuple(args))

    if graph is None:
        GetVal(obj, VT, *args)
    else:
        graph(obj, VT, *args)

    return set(children_iterator(node_id, child_VT, obj_type))


# -----------------------------------------------------------------------------
def leaves_iterator(node_id, get_val):
    stored = get_val(node_id[0], "StoredAttrs")

    for name, vt, args in onyx_dg.graph[node_id].children:
        if vt in stored:
            yield name, vt
        else:
            for leaf in leaves_iterator((name, vt, args), get_val):
                yield leaf


# -----------------------------------------------------------------------------
def LeafNodes(node_id, graph=None):
    """
    Description:
        Return all leaf-level nodes (StoredAttrs) of a given node.
    Inputs:
        node_id - parent node_id, in the form (Name, VT, args), where args can
                  be skipped in place of an empty tuple
        graph   - if set, function used to generate graph topology
    Yields:
        A set of nodes.
    """
    obj, VT, *args = node_id
    name = obj if isinstance(obj, str) else obj.Name
    node_id = (name, VT, tuple(args))

    get_val = graph or GetVal
    get_val(obj, VT, *args)

    return set(leaves_iterator(node_id, get_val))


# -----------------------------------------------------------------------------
def settable_iterator(node_id):
    for kid_id in onyx_dg.graph[node_id].children:
        node = onyx_dg.graph[kid_id]
        for leaf in settable_iterator(kid_id):
            if leaf is not None:
                yield leaf

        if isinstance(node, SettableNode):
            yield kid_id


# -----------------------------------------------------------------------------
def SettableNodes(node_id, graph=None):
    """
    Description:
        Return all settable children of a given node (stopping at the first
        level).
    Inputs:
        node_id - parent node_id, in the form (Name, VT, args), where args can
                  be skipped in place of an empty tuple
        graph   - if set, function used to generate graph topology
    Yields:
        A set of nodes.
    """
    obj, VT, *args = node_id
    name = obj if isinstance(obj, str) else obj.Name
    node_id = (name, VT, tuple(args))

    if graph is None:
        GetVal(obj, VT, *args)
    else:
        graph(obj, VT, *args)

    return set(settable_iterator(node_id))
