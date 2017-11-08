""" Marker Iterfaces for Epub
"""
from zope.interface import Interface

# Browser layer
from eea.epub.browser.interfaces import ILayer

# Events
from eea.epub.events.interfaces import IEPUBExportFail
from eea.epub.events.interfaces import IEPUBExportSuccess
from eea.epub.events.interfaces import IAsyncEPUBExportFail
from eea.epub.events.interfaces import IAsyncEPUBExportSuccess

#Subtypes
from eea.epub.subtypes.interfaces import IEPUBAware
from eea.epub.subtypes.interfaces import ICollectionEPUBAware

class IImportedBook(Interface):
    """ Marker interface for epub root folder """

class IImportedChapter(Interface):
    """ Marker interface for each imported chapter """

class IExportable(Interface):
    """ Marker interface for all epub exporable content types """

class IImportedImage(Interface):
    """ Marker interface for imported epub images """

__all__ = [
    ILayer.__name__,
    IEPUBExportFail.__name__,
    IEPUBExportSuccess.__name__,
    IAsyncEPUBExportFail.__name__,
    IAsyncEPUBExportSuccess.__name__,
    IEPUBAware.__name__,
    ICollectionEPUBAware.__name__,
]
