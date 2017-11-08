""" Relation vocabularies
"""
import operator
from zope.component import queryAdapter
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from eea.relations.interfaces import IToolAccessor
#
# Object provides
#
class ContentTypesVocabulary(object):
    """Vocabulary factory for object provides index.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """ See IVocabularyFactory interface
        """
        tool = queryAdapter(context, IToolAccessor)
        if not tool:
            return SimpleVocabulary([])

        items = [SimpleTerm(brain.getId, brain.getId, brain.Title)
                 for brain in tool.types()]
        return SimpleVocabulary(items)

class WorkflowStatesVocabulary(object):
    """ Vocabulary factory
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """ Return all unique states
        """
        wtool = getToolByName(context, 'portal_workflow')
        states = wtool.listWFStatesByTitle(filter_similar=True)
        states = dict((state, title or state)
                      for title, state in states).items()
        states.sort(key=operator.itemgetter(1))
        items = []
        for state, title in states:
            items.append(SimpleTerm(state, state, title))
        return SimpleVocabulary(items)
