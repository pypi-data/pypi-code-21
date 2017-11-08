""" Content
"""
from Products.CMFCore import utils as cmfutils
from Products.Archetypes.atapi import process_types, listTypes
from Products.Archetypes.atapi import registerType
from eea.geotags.content.demo import EEAGeotagsDemo, EEAGeotagsSimpleDemo
from eea.geotags.config import PROJECTNAME, ADD_CONTENT_PERMISSION

registerType(EEAGeotagsDemo, PROJECTNAME)
registerType(EEAGeotagsSimpleDemo, PROJECTNAME)

def initialize(context):
    """ Zope2 init
    """
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types=content_types,
        permission=ADD_CONTENT_PERMISSION,
        extra_constructors=constructors,
        fti=ftis,
        ).initialize(context)
