""" Interfaces
"""
from zope import schema
from zope.interface import Interface

class IGeoTaggable(Interface):
    """ Marker interface for content objects that can be geo tagged
    """

class IGeoTagged(Interface):
    """ Marker interface for content objects that received a geo tag
    """

class IGeoTags(Interface):
    """ Accessor/Mutator for geo tags annotations
    """
    tags = schema.Dict(title=u"Geojson tags")


    def getPoints(self):
        """ Returns a list of points as lat,long pairs in
        WGS 84 reference coordinate system.
        """
