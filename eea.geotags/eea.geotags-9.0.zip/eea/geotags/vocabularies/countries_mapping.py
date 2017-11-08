""" Countries
"""
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from eea.geotags.vocabularies.interfaces import IGeoCountriesMapping


class Countries_Mapping(object):
    """ Extract countries for group
    """
    implements(IGeoCountriesMapping)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        atvm = getToolByName(self.context, 'portal_vocabularies', '')
        voc = atvm.get('countries_mapping')
        if not voc:
            return SimpleVocabulary([])
        return voc
