""" google module """

from zope.interface import implements
from eea.google.tool.interfaces import IGoogleTool
from OFS.Folder import Folder

class GoogleTool(Folder):
    """ Google Tool
    """
    implements(IGoogleTool)
    id = 'portal_google'
    title = 'Manage Google API connections'
    meta_type = 'Google Tool'
    portal_type = 'Google Tool'
