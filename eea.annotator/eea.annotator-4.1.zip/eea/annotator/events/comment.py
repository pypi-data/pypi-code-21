""" Inline comments events
"""
from zope.interface import implements
from eea.annotator.events import interfaces

class InlineComment(object):
    """ Base Inline Comment event
    """
    implements(interfaces.IInlineComment)

    def __init__(self, context, **kwargs):
        self.object = context
        sdm = getattr(context, 'session_data_manager', None)
        session = sdm.getSessionData(create=True) if sdm else None

        for key, value in kwargs.items():
            setattr(self, key, value)
            if not session:
                continue
            session.set(key, value)

class InlineCommentAdded(InlineComment):
    """ Inline comment added
    """
    implements(interfaces.IInlineCommentAdded)

class InlineCommentModified(InlineComment):
    """ Inline comment modified
    """
    implements(interfaces.IInlineCommentModified)

class InlineCommentClosed(InlineComment):
    """ Inline comment closed
    """
    implements(interfaces.IInlineCommentClosed)

class InlineCommentOpened(InlineComment):
    """ Inline comment re-opened
    """
    implements(interfaces.IInlineCommentOpened)

class InlineCommentDeleted(InlineComment):
    """ Inline comment completely destroyed
    """
    implements(interfaces.IInlineCommentDeleted)

class InlineCommentReply(InlineComment):
    """ Reply added to inline comment
    """
    implements(interfaces.IInlineCommentReply)
