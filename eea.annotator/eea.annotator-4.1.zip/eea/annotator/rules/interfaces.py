""" Content rules interfaces
"""
from zope import schema
from zope.interface import Interface
from eea.annotator.config import EEAMessageFactory as _

class IAnnotatorAction(Interface):
    """ Custom content-rule action
    """
    disableAnnotator = schema.Bool(
        title=_(u'Disable inline comments'),
        description=_("Do not allow editors to add inline comments on "
                      'this context/page'))

    readOnlyAnnotator = schema.Bool(
        title=_('Read-only inline comments'),
        description=_("Make inline comments read-only"))
