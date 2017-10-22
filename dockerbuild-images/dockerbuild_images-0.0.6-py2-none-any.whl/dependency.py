# -*- coding: utf-8 -*-
import networkx as nx


noop = lambda e: True


def make_path(iterable_of_edges, condition=noop):
    '''
    >>> edges = [(1, 2), (2, 3), (3, 4)]
    >>> make_path(edges)
    >>> [4, 3, 2, 1]
    >>>
    >>> no_3 = lambda e: e != 3
    >>> make_path(edges, no_3)
    >>> [4, 2, 1]   # 3 was skipped

    PLEASE NOTE: path in the end is reversed
    '''
    path = []
    for e, d in iterable_of_edges:
        if e not in path and condition(e):
            path.append(e)
        if d not in path and condition(d):
            path.append(d)
    return list(reversed(path))


class BelongsToNodes(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def __call__(self, node):
        return node in self.nodes


def resolve(edges, relevant_nodes=None):
    relevant_nodes_provided = bool(relevant_nodes)
    relevant_nodes = relevant_nodes or []

    graph = nx.DiGraph()
    for e, v in edges:
        graph.add_edge(e, v)
        if not relevant_nodes_provided:
            relevant_nodes.append(e)
            relevant_nodes.append(v)

    condition = BelongsToNodes(relevant_nodes)

    ordered_paths = []
    for node in relevant_nodes:
        dfs_edges = nx.dfs_edges(graph, node)
        path = make_path(dfs_edges, condition)
        ordered_paths.append(path)
    ordered_paths.sort(key=lambda x: len(x))

    order = []
    for path in ordered_paths:
        for path_part in path:
            if path_part not in order:
                order.append(path_part)
    return order
