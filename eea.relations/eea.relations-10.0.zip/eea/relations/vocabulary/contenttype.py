""" Content-types vocabularies
"""
from zope.component import queryUtility
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
#
# Object provides
#
class ObjectProvidesVocabulary(object):
    """Vocabulary factory for object provides index.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """ See IVocabularyFactory interface
        """
        voc = queryUtility(IVocabularyFactory,
                           'eea.faceted.vocabularies.ObjectProvides')
        items = [SimpleTerm('', '', '')]
        if not voc:
            return SimpleVocabulary(items)

        voc = voc(context)
        items.extend(term for term in voc)
        return SimpleVocabulary(items)
#
# Portal Types
#
class PortalTypesVocabulary(object):
    """Vocabulary factory for portal types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        voc = queryUtility(IVocabularyFactory,
                           'eea.faceted.vocabularies.PortalTypes')
        items = [SimpleTerm('', '', '')]
        if not voc:
            return SimpleVocabulary(items)

        voc = voc(context)
        items.extend(term for term in voc)
        return SimpleVocabulary(items)
