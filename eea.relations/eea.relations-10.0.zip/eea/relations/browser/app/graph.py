""" Graph drawers
"""
from pydot import Dot as PyGraph
from zope.component import queryAdapter, queryUtility
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.relations.interfaces import INode
from eea.relations.interfaces import IEdge
from eea.relations.interfaces import IGraph
from eea.relations.interfaces import IToolAccessor

class BaseGraph(BrowserView):
    """ Abstract layer
    """
    def __init__(self, context, request):
        """ BaseGraph Init
        """
        super(BaseGraph, self).__init__(context, request)
        self._tool = None
        self._bad_relations = set()
        self._bad_content = set()
        self._graph = None
    #
    # Read-only properties
    #
    @property
    def bad_relations(self):
        """ Bad relations
        """
        return self._bad_relations

    @property
    def bad_content(self):
        """ Bad content
        """
        return self._bad_content

    @property
    def graph(self):
        """ Generate pydot.Graph
        """
        if self._graph is None:
            self._graph = PyGraph()
        return self._graph
    #
    # Utils
    #
    @property
    def tool(self):
        """ Portal relations tool
        """
        if not self._tool:
            self._tool = getToolByName(self.context, 'portal_relations')
        return self._tool
    #
    # Public interface
    #
    def image(self, setHeader=True, **kwargs):
        """ Returns a PNG image
        """
        converter = queryUtility(IGraph, name=u'png')
        raw = converter(self.graph)

        if setHeader:
            self.request.response.setHeader('Content-Type', 'image/png')
        return raw

    def json(self, setHeader=True, **kwargs):
        """ Returns a JSON graph
        """
        converter = queryUtility(IGraph, name=u'json')
        raw = converter(self.graph)

        if setHeader:
            self.request.response.setHeader('Content-Type', 'application/json')
        return raw

    def dot(self, setHeader=True, **kwargs):
        """ Return dotted graph
        """
        if setHeader:
            self.request.response.setHeader('Content-Type', 'text/plain')
        return self.graph.to_string()

    def __call__(self, *args, **kwargs):
        kwargs.update(self.request.form)
        setHeader = kwargs.get('setHeader', True)

        if self.__name__.endswith('.json'):
            return self.json(setHeader)
        elif self.__name__.endswith('.png'):
            return self.image(setHeader)
        return self.dot(setHeader)


class RelationGraph(BaseGraph):
    """ Draw a graph for Relation
    """
    @property
    def graph(self):
        """ Construct graph and mark broken relations if any
        """
        if self._graph is not None:
            return self._graph

        # Valid graph edge
        self._graph = PyGraph()

        value_from = self.context.getField('from').getAccessor(self.context)()
        nfrom = self.tool.get(value_from)
        if nfrom:
            node = queryAdapter(nfrom, INode)
            self._graph.add_node(node())
        else:
            self._bad_content.add(value_from)
            self._bad_relations.add(self.context.Title())

        value_to = self.context.getField('to').getAccessor(self.context)()
        nto = self.tool.get(value_to)
        if nto:
            if value_from != value_to:
                node = queryAdapter(nto, INode)
                self._graph.add_node(node())
        else:
            self._bad_content.add(value_to)
            self._bad_relations.add(self.context.Title())

        edge = queryAdapter(self.context, IEdge)()
        if edge:
            self._graph.add_edge(edge)

        return self._graph


class ContentTypeGraph(BaseGraph):
    """ Draw a graph for ContentType
    """

    @property
    def graph(self):
        """ Construct graph and mark broken relations if any
        """
        if self._graph is not None:
            return self._graph

        self._graph = PyGraph()

        # This node
        name = self.context.getId()
        node = queryAdapter(self.context, INode)
        self._graph.add_node(node())

        xtool = queryAdapter(self.context, IToolAccessor)
        for relation in xtool.relations(proxy=False):
            field = relation.getField('to')
            value_from = field.getAccessor(relation)()

            field = relation.getField('from')
            value_to = field.getAccessor(relation)()

            if name == value_from:
                nto = self.tool.get(value_to)
                if (value_from != value_to) and nto:
                    node = queryAdapter(nto, INode)
                    self._graph.add_node(node())
                edge = queryAdapter(relation, IEdge)()
                if edge:
                    self._graph.add_edge(edge)
                else:
                    self._bad_content.add(value_to)
                    self._bad_relations.add(relation.Title())

            elif name == value_to:
                nfrom = self.tool.get(value_from)
                if (value_from != value_to) and nfrom:
                    node = queryAdapter(nfrom, INode)
                    self._graph.add_node(node())
                edge = queryAdapter(relation, IEdge)()
                if edge:
                    self._graph.add_edge(edge)
                else:
                    self._bad_content.add(value_from)
                    self._bad_relations.add(relation.Title())

        return self._graph


class ToolGraph(BaseGraph):
    """ Draw a graph for portal_relations
    """

    @property
    def graph(self):
        """ Construct graph and mark broken relations if any
        """
        if self._graph is not None:
            return self._graph

        self._graph = PyGraph()

        xtool = queryAdapter(self.context, IToolAccessor)
        typesIds = set()
        for ctype in xtool.types(proxy=False):
            typesIds.add(ctype.getId())
            node = queryAdapter(ctype, INode)
            self._graph.add_node(node())

        for relation in xtool.relations(proxy=False):
            field = relation.getField('to')
            value_from = field.getAccessor(relation)()

            field = relation.getField('from')
            value_to = field.getAccessor(relation)()

            edge = queryAdapter(relation, IEdge)()
            if edge:
                self._graph.add_edge(edge)
            else:
                self._bad_relations.add(relation.Title())
                if value_from not in typesIds:
                    self._bad_content.add(value_from)
                if value_to not in typesIds:
                    self._bad_content.add(value_to)

        return self._graph
