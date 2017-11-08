""" Async events
"""

from zope.interface import implementer
from eea.epub.events.interfaces import IAsyncEPUBExportFail
from eea.epub.events.interfaces import IAsyncEPUBExportSuccess
from eea.converter.events.async import AsyncExportFail, AsyncExportSuccess

@implementer(IAsyncEPUBExportFail)
class AsyncEPUBExportFail(AsyncExportFail):
    """ Event triggered when an async EPUB export job failed
    """

@implementer(IAsyncEPUBExportSuccess)
class AsyncEPUBExportSuccess(AsyncExportSuccess):
    """ Event triggered when an async EPUB export job succeeded
    """
