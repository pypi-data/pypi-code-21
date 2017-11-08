""" Relations components
"""
from zope.component import queryAdapter
from eea.relations.interfaces import IToolAccessor

class RelationsLookUp(object):
    """ Lookup for possible relations
    """
    def __init__(self, context):
        self.context = context
        self._relations = []

    @property
    def relations(self):
        """ All possible relations
        """
        if self._relations:
            return self._relations

        tool = queryAdapter(self.context, IToolAccessor)
        if not tool:
            return self._relations

        self._relations = [doc for doc in tool.relations(proxy=False)]
        return self._relations

    def forward(self):
        """ Forward possible relations
        """
        name = self.context.getId()
        for relation in self.relations:
            nfrom = relation.getField('from').getAccessor(relation)()
            if name != nfrom:
                continue
            yield relation

    def backward(self):
        """ Backward possible relations
        """
        name = self.context.getId()
        for relation in self.relations:
            nto = relation.getField('to').getAccessor(relation)()
            if name != nto:
                continue
            yield relation

    def forward_with(self, who):
        """ Check content type to see if it's a forward
            relation for self.context
        """
        who_id = who.getId()
        for relation in self.forward():
            nto = relation.getField('to').getAccessor(relation)()
            if who_id == nto:
                return relation
        return None

    def backward_with(self, who):
        """ Check content type to see if it's a backward
            relation for self.context
        """
        who_id = who.getId()
        for relation in self.backward():
            nfrom = relation.getField('from').getAccessor(relation)()
            if who_id == nfrom:
                return relation
        return None
