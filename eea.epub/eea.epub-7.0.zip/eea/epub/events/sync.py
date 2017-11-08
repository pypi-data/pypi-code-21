""" Sync events
"""

from zope.interface import implementer
from eea.epub.events.interfaces import IEPUBExportFail
from eea.epub.events.interfaces import IEPUBExportSuccess
from eea.converter.events.sync import ExportFail, ExportSuccess

@implementer(IEPUBExportFail)
class EPUBExportFail(ExportFail):
    """ Event triggered when a ePub export job failed
    """

@implementer(IEPUBExportSuccess)
class EPUBExportSuccess(ExportSuccess):
    """ Event triggered when a ePub export job succeeded
    """
