""" EEA Geotags package
"""
from  eea.geotags import field
from eea.geotags import widget
from eea.geotags import content

def initialize(context):
    """ Zope 2 initialize
    """
    content.initialize(context)

__all__ = [field.__name__,
           widget.__name__]
