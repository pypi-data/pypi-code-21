""" Groups
"""
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from eea.geotags.vocabularies.interfaces import IGeoGroups

class Groups(object):
    """ Extract countries for group
    """
    implements(IGeoGroups)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        atvm = getToolByName(self.context, 'portal_vocabularies')
        if not 'geotags' in atvm.objectIds():
            return SimpleVocabulary([])

        voc = atvm['geotags']
        items = voc.objectItems()
        items = [SimpleTerm(key, key, item.title) for key, item in items]
        return SimpleVocabulary(items)
