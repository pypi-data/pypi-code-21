from collections import MutableSet

from . import helpers


FORWARD = 1     # used to look at Node children
BACKWARD = -1   # used to look at Node parents


class NodeSet(MutableSet):
    """
    A mutable set which automatically populates parent/child node sets.

    For example, if this NodeSet contains `children` nodes and a new node was added, that
    node's `parent` NodeSet will automatically be populated with the owner of this NodeSet.
    """

    def __init__(self, owner, items, direction):
        """
        :type owner: Node
        :type items: set[Node]
        :type direction: int
        """

        self.owner = owner
        self.items = set()
        self.direction = direction
        self.update(items)

    def __iter__(self):
        return self.items.__iter__()

    def __len__(self):
        return len(self.items)

    def add(self, value):
        """
        Adds the node to this NodeSet and populates the node's NodeSet with the owner
        of this NodeSet.

        :type value: Node
        """

        if value not in self:
            value.direction(self.direction * -1).items.add(self.owner)
        return self.items.add(value)

    def discard(self, value):
        """
        Removes the node from this NodeSet and removes this NodeSet's owner from the
        node's NodeSets.

        :type value: Node
        """

        if value in self:
            value.direction(self.direction * -1).items.discard(self.owner)
        return self.items.discard(value)

    def update(self, s):
        map(self.add, s)

    def discard_many(self, s):
        map(self.discard, s)

    def one(self, raise_on_empty=False):
        """
        Returns an item from this NodeSet if there is only one item.

        :type raise_on_empty: bool
        :rtype: Node | None
        :raises: ValueError
        """

        if not self.items and raise_on_empty:
            raise ValueError('Called NodeSet.one on empty set')
        elif len(self.items) > 1:
            raise ValueError('Called NodeSet.one on set with multiple values')

        return next(iter(self.items), None)

    def __contains__(self, x):
        return self.items.__contains__(x)

    def __repr__(self):
        return 'NodeSet{}'.format(tuple(self.items))


class Node(object):

    def __init__(self, data=None, parents=None, children=None):
        self.parents = NodeSet(self, [] if parents is None else parents, BACKWARD)
        self.children = NodeSet(self, [] if children is None else children, FORWARD)
        self.data = data

    def __repr__(self):
        return '<Node {}>'.format(self.data)

    @property
    def connections(self):
        """
        Returns all parents and children associated with this Node.

        :rtype: set[Node]
        """

        return set(list(self.parents) + list(self.children))

    def direction(self, direction):
        """
        Returns this node's parents if direction is BACKWARD, else, returns children nodes.

        :int direction: int
        :rtype: NodeSet
        """

        return self.parents if direction == BACKWARD else self.children

    def depth_first_traversal(self, callback, direction, obj=None):
        """
        Executes a depth-first traversal from this node in a given direction. Raising
        a StopIteration will terminate the traversal.

        :type callback: (Node, object) -> ()
        :type direction: int
        :type obj: Any
        :return: Returns `obj` (or None if no `obj` is supplied).
        :rtype: Any
        """

        return helpers.depth_first_traversal_for_node(node=self, callback=callback, direction=direction, obj=obj)

    def breadth_first_traversal(self, callback, direction, obj=None):
        """
        Executes a breadth-first traversal from this node in a given direction. Raising
        a StopIteration will terminate the traversal.

        :type callback: (Node, object) -> ()
        :type direction: int
        :type obj: Any
        :return: Returns `obj` (or None if no `obj` is supplied).
        :rtype: Any
        """

        return helpers.breadth_first_traversal_for_node(node=self, callback=callback, direction=direction, obj=obj)

    def walk_links(self, callback, direction, obj=None):
        """
        Walks the each link for this node. Raising a StopIteration will terminate the
        traversal.

        :type callback: (Node, Node, object) -> ()
        :type direction: int
        :type obj: Any
        :return: Returns `obj` (or None if no `obj` is supplied).
        :rtype: Any
        """

        return helpers.walk_links_for_node(node=self, callback=callback, direction=direction, obj=obj)

    def root(self):
        """
        Returns the root node of this node if it only has one root node.

        :rtype: Node
        :raises: ValueError
        """

        roots = self.roots()
        if len(roots) > 1:
            raise ValueError('Node.root is not applicable when the node has multiple roots')

        return next(iter(roots))

    def gather_nodes(self, direction=None):
        """
        Returns all nodes in the tree. Nodes can be restricted by specifying a direction.

        :type direction: int
        :rtype: set[Node]
        """

        return helpers.gather_nodes(node=self, direction=direction)

    def flatten(self, direction=None):
        """
        Returns a list of node lists representing a path on the tree.

        :type direction: int | None
        :rtype: list[list[treestruct.Node]]
        """

        return helpers.flatten_from_node(node=self, direction=direction)

    def roots(self):
        """
        Returns all roots (any parent nodes with no parents) of this node.

        :rtype: set[Node]
        """

        return helpers.roots_for_node(node=self)

    def leaves(self):
        """
        Returns all leaves (any child nodes with no children) of this node.

        :rtype: set[Node]
        """

        return helpers.leaves_for_node(node=self)

    def delete(self, direction=None):
        """
        Removes this node from the NodeSets of connected nodes. If direction is
        given, only remove the node from the connected nodes in the given direction.

        :type direction: int
        :rtype: Node
        """

        return helpers.delete_node_relationships(node=self, direction=direction)

    def clone(self):
        """
        Clones the node and all its child nodes and forms a new root.

        :rtype: Node
        """

        return helpers.clone_subtree(node=self)

    def find_all(self, condition, direction=None):
        """
        Returns all nodes which match the given condition.

        :type condition: (Node) -> bool
        :type direction: int
        :rtype: set[Node]
        """

        return helpers.find_nodes(node=self, condition=condition, direction=direction)

    def find(self, condition, direction=None, raise_on_empty=False):
        """
        Returns a single node which matches the given condition.

        :type condition: (Node) -> bool
        :type direction: int
        :type raise_on_empty: bool
        :rtype: Node | None
        :raises: ValueError
        """

        return helpers.find_node(node=self, condition=condition, direction=direction, raise_on_empty=raise_on_empty)

    def to_dict(self, data_converter=None):
        """
        Converts this node's complete structure into a dictionary.

        :type data_converter: (Any) -> (Any) | None
        :rtype: list[dict]
        """

        return helpers.to_dict_from_node(node=self, data_converter=data_converter)

    @classmethod
    def from_dict(cls, tree_dict, data_converter=None):
        """
        Converts a dict into a tree of Nodes, with the return value being the
        root node.

        :param tree_dict: dict
        :type data_converter: (Any) -> (Any) | None
        :rtype: Node
        """

        return helpers.from_dict(tree_dict=tree_dict, data_converter=data_converter)

    @classmethod
    def from_nodes(cls, nodes):
        """
        Creates a flat tree structure from a list of nodes. It is assumed that the first Node
        in the list is the root and each subsequent Node is a child. Any existing parents or
        children will be disregarded.

        :type nodes: collections.Iterable[Node]
        :rtype: Node
        """

        return helpers.node_from_node_sequence(nodes)
