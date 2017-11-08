""" Annotator events
"""

from zope.component.interfaces import IObjectEvent

class IAnnotatorEvent(IObjectEvent):
    """ Base Event Interface for all annotator events
    """

class IInlineComment(IAnnotatorEvent):
    """ One Inline comment event
    """

class IInlineCommentAdded(IInlineComment):
    """ Inline comment added
    """

class IInlineCommentModified(IInlineComment):
    """ Inline comment modified
    """

class IInlineCommentClosed(IInlineComment):
    """ Inline comment closed
    """

class IInlineCommentOpened(IInlineComment):
    """ Inline comment re-opened
    """

class IInlineCommentDeleted(IInlineComment):
    """ Inline comment deleted
    """

class IInlineCommentReply(IInlineComment):
    """ Reply added to inline comment
    """
