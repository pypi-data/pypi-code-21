""" Groups
"""
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from eea.geotags.vocabularies.interfaces import IBioGroups

class BioGroups(object):
    """ Biogeographical regions
    """
    implements(IBioGroups)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        atvm = getToolByName(self.context, 'portal_vocabularies')
        if not 'biotags' in atvm.objectIds():
            return SimpleVocabulary([])

        voc = atvm['biotags']
        items = voc.objectItems()
        items = [SimpleTerm(key, key, item.title) for key, item in items]
        return SimpleVocabulary(items)
