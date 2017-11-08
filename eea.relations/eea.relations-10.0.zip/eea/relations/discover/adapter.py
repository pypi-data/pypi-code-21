""" Auto-discover adapters
"""
from zope.interface import implements
from eea.relations.discover.interfaces import IAutoRelations

class AutoRelations(object):
    """ Abstract adapter to auto discover context relations
    """
    implements(IAutoRelations)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        """ Return a list of labeled brains/objects, like
            [('Data used in figures',databrains),
             ('People responsible',peoplebrains)]
        """
        return []
