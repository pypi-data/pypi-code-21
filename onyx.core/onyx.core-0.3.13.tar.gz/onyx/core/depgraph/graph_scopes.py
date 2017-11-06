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

from .graph import DependencyGraph, GraphError, PropertyNode, SettableNode
from .graph import create_node

from .. import depgraph as onyx_dg

import collections

__all__ = ["EvalBlock", "GraphScope"]


###############################################################################
class EvalBlock(object):
    """
    Description:
        Context manager used to manage lifetime of one or more one-off changes.
    Usage:
        Typical use is as follows:

        with EvalBlock() as eb:
            ...
            eb.change_value("abc", "xyz", 123)
            ...
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        self.__changes = []
        self.__changed_nodes = {}

    # -------------------------------------------------------------------------
    def __enter__(self):
        # --- return a reference to itself (to be used by change_value)
        return self

    # -------------------------------------------------------------------------
    def __exit__(self, *args, **kwds):
        for node_id in reversed(self.__changes):
            old_node = self.__changed_nodes[node_id]

            # --- invalidate all parents, but not the node itself
            for parent in onyx_dg.graph[node_id].parents | old_node.parents:
                onyx_dg.graph[parent].invalidate()

            # --- reconstruct connection with children
            for child in old_node.children:
                onyx_dg.graph[child].parents.add(node_id)

            # --- store pre-change node into the graph
            onyx_dg.graph[node_id] = old_node

        self.__changes = []
        self.__changed_nodes = {}

        # --- returns False so that all execptions raised will be propagated
        return False

    # -------------------------------------------------------------------------
    def change_value(self, obj, VT, value):
        """
        Description:
            Change the in-memory value of a ValueType within an EvalBlock.
        Inputs:
            obj   - instance (or name) of an object derived from UfoBase
            VT    - name of the target ValueType
            value - the new value for the VT
        Returns:
            None.
        """
        name = obj if isinstance(obj, str) else obj.Name
        node_id = (name, VT, ())
        new_node = False

        try:
            node = onyx_dg.graph[node_id]
        except KeyError:
            new_node = True
            onyx_dg.graph[node_id] = node = create_node(node_id)

        if not isinstance(node, (PropertyNode, SettableNode)):
            raise GraphError("Unsupported node type: "
                             "{0:s}".format(node.__class__.__name__))

        # --- copy pre-change node and store it in __changed_nodes. This is
        #     only required the first time a VT is changed.
        if node_id not in self.__changed_nodes:
            self.__changes.append(node_id)
            self.__changed_nodes[node_id] = node.clone()

        if not new_node:
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


###############################################################################
class dict_with_fallback(collections.UserDict):
    # -------------------------------------------------------------------------
    def __init__(self, fallback, *args, **kwds):
        super().__init__(*args, **kwds)
        self.fallback = fallback

    # -------------------------------------------------------------------------
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return self.fallback[item]


###############################################################################
class GraphScope(DependencyGraph):
    """
    Description:
        Context manager used to manage the lifetime of in-memory changes to
        ValueTypes. GraphScope can be used to create persistent scenarions that
        are then re-used multiple times.
    Usage:
        Typical use is as follows:

        scope = GraphScope()
        scope.change_value("abc", xyz", 123)
        with scope:
            ...
            scope.change_value("abc", "xxx", 666)
            ...

        with scope:
            ...
            ...
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        # --- the GraphScope keeps track of references to the underlying graph
        #     at the time when a new GraphScope instance is created
        self.udl_graph = onyx_dg.graph
        self.vts_by_obj = dict_with_fallback(onyx_dg.graph.vts_by_obj)

        # --- used to determine if the GraphScope is being used as a context
        #     manager
        self.__active = False
        # --- when GraphScope is being used as a context manager it becomes
        #     the global graph instance and a reference to the previous graph
        #     instance is stored here.
        self.__last_graph = None

    # -------------------------------------------------------------------------
    def __enter__(self):
        self.__active = True
        self.__last_graph = onyx_dg.graph
        onyx_dg.graph = self
        # --- return a reference to itself (to be used for disposable scopes)
        return self

    # -------------------------------------------------------------------------
    def __exit__(self, *args, **kwds):
        onyx_dg.graph = self.__last_graph
        self.__active = False
        self.__last_graph = None
        # --- returns False so that all execptions raised will be propagated
        return False

    # -------------------------------------------------------------------------
    def __deepcopy__(self, memo):
        clone = self.__new__(self.__class__)
        clone.data = self.data.copy()
        clone.udl_graph = self.udl_graph
        clone.vts_by_obj = self.vts_by_obj.copy()
        clone.__active = self.__active
        clone.__last_graph = self.__last_graph
        memo[id(self)] = clone
        return clone

    # -------------------------------------------------------------------------
    def __getitem__(self, node_id):
        try:
            return super().__getitem__(node_id)
        except KeyError:
            return self.udl_graph[node_id]

    # -------------------------------------------------------------------------
    def __copy_and_invalidate(self, node_id):
        try:
            node = super().__getitem__(node_id)
            node.valid = False
        except KeyError:
            try:
                node = self.udl_graph[node_id].clone()
                node.valid = False
            except KeyError:
                node = create_node(node_id)

            self[node_id] = node

        for parent in node.parents:
            self.__copy_and_invalidate(parent)

        return node

    # -------------------------------------------------------------------------
    def change_value(self, obj, VT, value):
        """
        Description:
            Change the value of a ValueType within a GraphScope.
            NB: only StoredAttrs and VTs defined as Property can be changed.
        Inputs:
            obj   - instance (or name) of an object derived from UfoBase
            VT    - name of the target ValueType
            value - the new value for the VT
        Returns:
            None.
        """
        if not self.__active:
            # --- switch graph to graph scope
            self.__last_graph = onyx_dg.graph
            onyx_dg.graph = self

        name = obj if isinstance(obj, str) else obj.Name
        node_id = (name, VT, ())

        # --- create a local copy (local to the GraphScope) of the sub-graph
        #     that depends on the changed node as well as the immediate
        #     children of the copied nodes.
        #     NB: all nodes are created anew, they are invalid and sub-graph
        #         topology is undefined.
        node = self.__copy_and_invalidate(node_id)

        if not isinstance(node, (PropertyNode, SettableNode)):
            raise GraphError("Unsupported node type: "
                             "{0:s}".format(node.__class__.__name__))

        # --- set the node value and set its state to valid
        node.value = value
        node.valid = True

        if not self.__active:
            # --- switch graph back to the fallback
            onyx_dg.graph = self.__last_graph
            self.__last_graph = None
