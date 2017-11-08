""" Graph utilities
"""
import os
import json
from tempfile import mktemp
from zope.interface import implements
from eea.relations.graph.interfaces import IGraph
from eea.relations.config import GRAPHVIZ_PATHS

class Graph(object):
    """ Generates a PNG graph
    """
    implements(IGraph)

    def __init__(self, fmt='png'):
        self.fmt = fmt

    def __call__(self, graph):
        """ Draw pydot.Graph
        """
        if GRAPHVIZ_PATHS:
            graph.progs = GRAPHVIZ_PATHS

        writter = getattr(graph, 'write_' + self.fmt, None)
        if not writter:
            return None

        path = mktemp('.%s'  % self.fmt)
        img = writter(path=path)

        img = open(path, 'rb')
        raw = img.read()

        img.close()
        os.remove(path)

        return raw

class JSONGraph(object):
    """ Export Graph to JSON
    """
    implements(IGraph)

    def __init__(self, fmt='json'):
        self.fmt = fmt

    def __call__(self, graph):
        """ Draw json Graph
        """
        res = {
            'nodes': [],
            'edges': []
        }

        for node in graph.get_nodes():
            res['nodes'].append({
                'name': node.get_name().strip('"'),
                'label': node.get_label().strip('"')
            })

        for edge in graph.get_edges():
            source = edge.get_source()
            source = source.strip('"') if source else ""
            destination = edge.get_destination()
            destination = destination.strip('"') if destination else ""
            label = edge.get_label()
            label = label.strip('"') if label else ""
            fontcolor = edge.get_fontcolor() or ""
            color = edge.get_color() or ""
            res['edges'].append({
                'source': source,
                'destination': destination,
                'label': label,
                'fontcolor': fontcolor,
                'color': color
            })

        return json.dumps(res)
