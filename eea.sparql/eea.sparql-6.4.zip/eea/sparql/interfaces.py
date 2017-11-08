""" Sparql interfaces module
"""

from zope.interface import Interface
from zope.component.interfaces import IObjectEvent

class ISparql(Interface):
    """ISparql"""

class ISparqlBookmarksFolder(ISparql):
    """ISparqlBookmarksFolder"""

class ISparqlBookmarksFolderAdded(IObjectEvent):
    """An event signalling that the sparql bookmarks folder was added
    """
