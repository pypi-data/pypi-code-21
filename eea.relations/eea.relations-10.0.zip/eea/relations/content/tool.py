""" Relations tool
"""
from zope.interface import implements
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.Archetypes.atapi import OrderedBaseFolder
from Products.Archetypes.atapi import OrderedBaseFolderSchema
from Products.Archetypes.atapi import Schema
from eea.relations.content.interfaces import IRelationsTool, IToolAccessor

class EEARelationsTool(UniqueObject, OrderedBaseFolder):
    """ Local utility to store and customize possible content types relations
    """
    implements(IRelationsTool)

    meta_type = "EEARelationsTool"

    id_field = OrderedBaseFolderSchema['id'].copy()
    id_field.mode = 'r'
    title_field = OrderedBaseFolderSchema['title'].copy()
    title_field.mode = 'r'

    manage_options = OrderedBaseFolder.manage_options

    schema = OrderedBaseFolderSchema  + Schema((
        id_field,
        title_field,
        ),
    )

class RelationsToolAccessor(object):
    """ Get tool properties
    """
    implements(IToolAccessor)

    def __init__(self, context):
        self.context = getToolByName(context, 'portal_relations', context)

    def relations(self, proxy=True, **kwargs):
        """ Possible relations
        """
        kwargs.setdefault('portal_type', 'EEAPossibleRelation')
        kwargs.setdefault('review_state', '')
        brains = self.context.getFolderContents(contentFilter=kwargs)
        for brain in brains:
            if not proxy:
                brain = brain.getObject()
            if brain:
                yield brain

    def types(self, proxy=True, **kwargs):
        """ Content types
        """
        kwargs.setdefault('portal_type', 'EEARelationsContentType')
        kwargs.setdefault('review_state', '')

        # 75296 context does not have access to getFolderContent within an
        # async instance
        hasFolderContents = getattr(self.context, 'getFolderContents',
                lambda contentFilter=None: '')
        if not hasFolderContents:
            yield ""

        brains = self.context.getFolderContents(contentFilter=kwargs)
        for brain in brains:
            if not proxy:
                brain = brain.getObject()
            if brain:
                yield brain
