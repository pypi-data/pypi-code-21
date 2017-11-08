""" Custom storage
"""
from zope.interface import implements
from eea.faceted.tool.interfaces import IPortalType
from OFS.Folder import Folder

class PortalType(Folder):
    """ Storage for custom portal types
    """
    implements(IPortalType)
    meta_type = 'EEA Faceted Portal Type'
    _properties = (
        {'id':'title', 'type': 'string', 'mode':'w'},
        {'id':'search_interface', 'type': 'string', 'mode':'w'},
        {'id':'search_type', 'type': 'string', 'mode':'w'},
    )

    title = ''
    search_interface = ''
    search_type = ''
