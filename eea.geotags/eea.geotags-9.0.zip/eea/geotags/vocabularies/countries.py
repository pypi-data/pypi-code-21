""" Countries
"""
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from eea.geotags.vocabularies.interfaces import IGeoCountries

class Countries(object):
    """ Extract countries for group
    """
    implements(IGeoCountries)

    def __init__(self, context):
        self.context = context

    def __call__(self, group=''):
        if not group:
            return SimpleVocabulary([])

        atvm = getToolByName(self.context, 'portal_vocabularies')
        if not 'geotags' in atvm.objectIds():
            return SimpleVocabulary([])

        voc = atvm['geotags']
        if not group in voc.objectIds():
            return SimpleVocabulary([])

        voc = voc[group]
        items = [SimpleTerm(key, key, item.title)
                        for key, item in voc.objectItems()]
        return SimpleVocabulary(items)
