""" Subtyping interfaces
"""
from zope.interface import Interface

class IEPUBAware(Interface):
    """ Objects which can be downloaded as ePub.
    """

class ICollectionEPUBAware(IEPUBAware):
    """ Collections of objects which can be downloaded as ePub.
    """
