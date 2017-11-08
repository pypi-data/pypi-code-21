""" Events
"""
from eea.converter.interfaces import IExportFail, IExportSuccess
from eea.converter.interfaces import IAsyncExportFail, IAsyncExportSuccess

class IEPUBExportSuccess(IExportSuccess):
    """ ePub export succeeded
    """

class IEPUBExportFail(IExportFail):
    """ ePub export failed
    """

class IAsyncEPUBExportSuccess(IAsyncExportSuccess):
    """ Async job for ePub export succeeded
    """

class IAsyncEPUBExportFail(IAsyncExportFail):
    """ Async job for ePub export failed
    """
