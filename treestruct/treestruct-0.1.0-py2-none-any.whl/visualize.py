import treestruct
import graphviz


def _build_walk_formatter(fmt):
    def formatter(a, b, graph):
        af = fmt(a.data)
        bf = fmt(b.data)
        graph.node(af)
        graph.node(bf)
        graph.edge(af, bf)

    return formatter


class Graph(object):

    def __init__(self, node, **options):
        self.node = treestruct.helpers.clone_subtree(node)
        self.graph = graphviz.Digraph(**options)
        self.__did_draw = False

    def defaults(self, **attributes):
        for key, value in attributes.iteritems():
            if isinstance(value, dict):
                self.graph.attr(key, **value)
            else:
                self.graph.attr(**{key: value})

    def draw_links(self, node_formatter=None):
        self.draw_links_with_formatter(_build_walk_formatter(node_formatter or str))

    def draw_links_with_formatter(self, formatter):
        self.__did_draw = True
        self.node.walk_links(callback=formatter, direction=treestruct.FORWARD, obj=self.graph)

    def draw_via_traversal(self, formatter):
        self.__did_draw = True
        self.node.depth_first_traversal(callback=formatter, direction=treestruct.FORWARD, obj=self.graph)

    def save(self, **options):
        self._output_func(self.graph.save, **options)

    def render(self, **options):
        self._output_func(self.graph.render, **options)

    def view(self, **options):
        self._output_func(self.graph.view, **options)

    def _output_func(self, func, **options):
        if not self.__did_draw:
            self.draw_links()
        func(**options)


def simple_graph(node, options=None, node_formatter=None):
    graph = Graph(node)
    graph.defaults(**options or {})
    graph.draw_links(node_formatter)
    return graph


def view_graph(node, options=None, node_formatter=None):
    return simple_graph(node, options, node_formatter).view()


def view_inline(node, options=None, node_formatter=None):
    return simple_graph(node, options, node_formatter).graph
