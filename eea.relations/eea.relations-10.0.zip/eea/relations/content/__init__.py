""" Content
"""
from Products.CMFCore import utils as cmfutils
from Products.Archetypes.atapi import process_types, listTypes
from Products.Archetypes.atapi import registerType
from eea.relations.content.tool import EEARelationsTool
from eea.relations.content.contenttype import EEARelationsContentType
from eea.relations.content.relation import EEAPossibleRelation
from eea.relations.config import (
    PROJECTNAME,
    ADD_CONTENT_PERMISSION
)

registerType(EEARelationsTool, PROJECTNAME)
registerType(EEARelationsContentType, PROJECTNAME)
registerType(EEAPossibleRelation, PROJECTNAME)

def initialize(context):
    """ Zope 2
    """
    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                      PROJECTNAME)

    cmfutils.ToolInit(PROJECTNAME + ' Tools',
                tools=[EEARelationsTool],
                icon='content/tool.gif'
                ).initialize(context)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types=content_types,
        permission=ADD_CONTENT_PERMISSION,
        extra_constructors=constructors,
        fti=ftis,
        ).initialize(context)
