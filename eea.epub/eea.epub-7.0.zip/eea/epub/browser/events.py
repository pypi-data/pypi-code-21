""" Event registration useful only in the context of EEA where
    our Epub folders should also provide INavigationRoot
"""
from zope.component.interfaces import IObjectEvent
from zope.interface import alsoProvides
from zope.interface import implements
from plone.app.layout.navigation.interfaces import INavigationRoot

class IEpubImportedEvent(IObjectEvent):
    """ Event interface which signals that a epub was imported
    """

class EpubImportedEvent(object):
    """ Sent if an epub file was imported
    """
    implements(IEpubImportedEvent)

    def __init__(self, context, **kwargs):
        self.object = context

def handle_epub_import(obj):
    """ Make our epub folder also provide INavigationRoot
    """
    alsoProvides(obj.object, INavigationRoot)
