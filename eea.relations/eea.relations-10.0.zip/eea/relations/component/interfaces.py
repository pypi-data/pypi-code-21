""" EEA relations components interfaces
"""
from zope.interface import Interface

class IContentTypeLookUp(Interface):
    """ Lookup object in portal_relations content-types
    """

class IRelationsLookUp(Interface):
    """ Lookup for possible relations
    """
    def forward():
        """ Forward relations
        """

    def backward():
        """ Backward relations
        """

    def forward_with(who):
        """ Get forward relation with "who"
        """

    def backward_with(who):
        """ Get backward relation with "who"
        """
