""" Subtyping interfaces
"""
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.interface import Interface

class IAnnotatorAware(Interface):
    """ Objects which are eea.annotator aware
    """

class IDexterityAnnotatorAware(IAnnotatorAware):
    """ Dexterity objects which are eea.annotator aware
    """

__all__ = [
    IAnnotations.__name__,
    AttributeAnnotations.__name__
]
