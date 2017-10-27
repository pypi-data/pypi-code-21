from contextlib import contextmanager

import flask

__all__ = [
    'draft',
    'published'
]


class ContextManager:
    """
    The standard manager class for managing draft and published contexts.
    """

    def __init__(self, key='__draft__'):

        # The key used to store the draft/published state of the context
        self.key = key

    @property
    def is_draft(self):
        """Return True if the context is currently draft"""
        return flask.g.get(self.key, True) == True

    @property
    def is_published(self):
        """Return True if the context is currently published"""
        return flask.g.get(self.key, True) == False

    def set_context(draft=False, published=False):
        """
        Set the context manually. Manually setting the context means the the
        context is not automatically reset when the context is left.

        Rule of thumb only set the context manually if you know what you're
        doing. This method was added to allow us to set the context at the
        start of a chain and then we use the final function to reset the
        context.

        Example usage:

            manager.set_context(published=True)

        """
        assert (not (draft or published)) or (draft and published), \
                'You must specify draft True or published as True'

        setattr(flask.g, self.key, not draft)

    @contextmanager
    def draft(self):
        """Set the context to use the draft context"""
        context = self.is_draft
        try:
            setattr(flask.g, self.key, True)
            yield
        finally:
            setattr(flask.g, self.key, context)

    @contextmanager
    def published(self):
        """Set the context to use the published context"""
        context = self.is_draft
        try:
            setattr(flask.g, self.key, False)
            yield
        finally:
            setattr(flask.g, self.key, context)
