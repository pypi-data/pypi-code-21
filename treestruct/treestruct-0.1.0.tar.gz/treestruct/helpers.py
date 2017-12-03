import treestruct


def leaves_for_node(node):
    """
    Returns all roots (any child nodes with no children) for the given node.

    :type node: treestruct.Node
    :rtype: set[treestruct.Node]
    """
    return _absolutes(node, treestruct.FORWARD)


def roots_for_node(node):
    """
    Returns all roots (any parent nodes with no parents) for the given node.

    :type node: treestruct.Node
    :rtype: set[treestruct.Node]
    """
    return _absolutes(node, treestruct.BACKWARD)


def walk_links_for_node(node, callback, direction, obj=None):
    """
    Walks the each link from the given node. Raising a StopIteration will terminate the
    traversal.

    :type node: treestruct.Node
    :type callback: (treestruct.Node, treestruct.Node, object) -> ()
    :type direction: int
    :type obj: Any
    :return: Returns `obj` (or None if no `obj` is supplied).
    :rtype: Any
    """

    try:
        visited = set()
        queue = [node]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            for connected_node in node.direction(direction):
                callback(node, connected_node, obj)
                queue.append(connected_node)
    except StopIteration:
        pass
    return obj


def depth_first_traversal_for_node(node, callback, direction, obj=None):
    """
    Executes a depth-first traversal from this node in a given direction. Raising
    a StopIteration will terminate the traversal.

    :type node: treestruct.Node
    :type callback: (treestruct.Node, treestruct.Node, object) -> ()
    :type direction: int
    :type obj: Any
    :return: Returns `obj` (or None if no `obj` is supplied).
    :rtype: Any
    """

    return _traverse(node, -1, callback, direction, obj)


def breadth_first_traversal_for_node(node, callback, direction, obj=None):
    """
    Executes a breadth-first traversal from this node in a given direction. Raising
    a StopIteration will terminate the traversal.

    :type node: treestruct.Node
    :type callback: (treestruct.Node, treestruct.Node, object) -> ()
    :type direction: int
    :type obj: Any
    :return: Returns `obj` (or None if no `obj` is supplied).
    :rtype: Any
    """

    return _traverse(node, 0, callback, direction, obj)


def _absolutes(node, direction):
    nodes = set()
    node.depth_first_traversal(lambda n, l: l.add(n) if not n.direction(direction) else None, direction, nodes)
    return nodes


def _traverse(node, pop_idx, callback, direction, obj=None):
    try:
        visited = set()
        struct = [node]
        while struct:
            node = struct.pop(pop_idx)
            if node in visited:
                continue
            visited.add(node)
            struct += list(node.direction(direction))
            callback(node, obj)
    except StopIteration:
        pass
    return obj


def find_nodes(node, condition, direction=None):
    """
    Returns all nodes which match the given condition.

    :type node: treestruct.Node
    :type condition: (treestruct.Node) -> bool
    :type direction: int
    :rtype: set[treestruct.Node]
    :raises: ValueError
    """

    return {n for n in gather_nodes(node, direction) if condition(n)}


def find_node(node, condition, direction, raise_on_empty):
    """
    Returns a single node which matches the given condition.

    :type node: treestruct.Node
    :type condition: (treestruct.Node) -> bool
    :type direction: int
    :type raise_on_empty: bool
    :rtype: treestruct.Node | None
    :raises: ValueError
    """

    matches = find_nodes(node, condition, direction)

    if not matches and raise_on_empty:
        raise ValueError('Called NodeSet.one on empty set')
    elif len(matches) > 1:
        raise ValueError('Called NodeSet.one on set with multiple values')

    return next(iter(matches), None)


def gather_nodes(node, direction=None):
    """
    Returns all nodes in the tree. Nodes can be restricted by specifying a direction.

    :type direction: int
    :rtype: set[treestruct.Node]
    """

    start_points = node.roots() if direction is None else [node]
    nodes = set()

    for start_point in start_points:
        start_point.depth_first_traversal(lambda n, o: o.add(n), direction or treestruct.FORWARD, nodes)

    return nodes


def flatten_from_node(node, direction=None):
    """
    Returns a list of node lists representing a path on the tree.

    :type node: treestruct.Node
    :type direction: int | None
    :rtype: list[list[treestruct.Node]]
    """

    start_points = node.leaves() if direction is None else [node]
    flattened_lists = []

    for start_point in start_points:
        flattened_list = start_point.depth_first_traversal(lambda n, l: l.append(n), direction or treestruct.BACKWARD, [])
        if any(n for n in flattened_list if len(n.parents) > 1):
            raise Exception('Flattening nodes with multiple parents is not supported at the moment')
        if direction != treestruct.FORWARD:
            flattened_list = flattened_list[::-1]
        flattened_lists.append(flattened_list)

    return flattened_lists


def to_dict_from_node(node, data_converter=None):
    """
    Converts the node structure into a dictionary.

    :type node: treestruct.Node
    :type data_converter: (Any) -> (Any) | None
    :rtype: list[dict]
    """

    data_converter = (lambda n: n) if data_converter is None else data_converter
    roots = node.roots() or [node]

    def _convert(n, converter):
        return {
            'data': converter(n.data),
            'children': [_convert(c, converter) for c in n.children]
        }

    return [_convert(root, data_converter) for root in roots]


def from_dict(tree_dict, data_converter=None):
    """
    Converts a dict into a tree of Nodes, with the return value being the
    root node.

    :param tree_dict: dict
    :type data_converter: (Any) -> (Any) | None
    :rtype: treestruct.Node
    """

    data_converter = (lambda n: n) if data_converter is None else data_converter

    def _build_tree(struct, converter):
        node = treestruct.Node(converter(struct['data']))
        for child_struct in struct.get('children'):
            node.children.add(_build_tree(child_struct, converter))
        return node

    return _build_tree(tree_dict, data_converter)


def delete_node_relationships(node, direction=None):
    """
    Removes the given node from the NodeSets of connected nodes. If direction is
    given, only remove the node from the connected nodes in the given direction.

    :type node: treestruct.Node
    :type direction: int
    :rtype: treestruct.Node
    """

    if direction in (None, treestruct.BACKWARD):
        for parent in tuple(node.parents):
            parent.children.discard(node)

    if direction in (None, treestruct.FORWARD):
        for child in tuple(node.children):
            node.children.discard(child)

    return node


def clone_subtree(node):
    """
    Clones the node and all its child nodes and forms a new root.

    :type node: Node
    :rtype: Node
    """
    return treestruct.Node(node.data, children=map(clone_subtree, node.children))


def node_from_node_sequence(nodes):
    """
    Creates a flat tree structure from a list of nodes. It is assumed that the first Node
    in the list is the root and each subsequent Node is a child. Any existing parents or
    children will be disregarded.

    :type nodes: collections.Iterable[treestruct.Node]
    :rtype: treestruct.Node
    """

    if not nodes:
        return None
    child = node_from_node_sequence(nodes[1:])
    return treestruct.Node(data=nodes[0].data, children=[child] if child else [])