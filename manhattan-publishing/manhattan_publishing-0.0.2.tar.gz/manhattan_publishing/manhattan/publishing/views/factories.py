"""
Link factories for content views.
"""

import json

import flask
from manhattan.content.snippets import Snippet
from manhattan.manage.views import utils as manage_utils
import re

__all__ = [
    'reset_context',
    'set_context'
    ]


def reset_context():
    """
    Return a function that will reset the publishing context to the state
    before it was last set.
    """

    def reset_context(state):
        context_manager = state.manage_config.frame_cls._context_manager
        draft = state._initial_publishing_context
        published = not state._initial_publishing_context
        context_manage.set_context(draft, published)

    return reset_context

def set_context(draft=False, published=False):
    """
    Return a function that sets the publishing context to the given context
    ('draft' or 'published').

    This link adds the `_initial_publishing_context` to the state which
    contains the context before the switch.
    """

    def set_context(state):
        context_manager = state.manage_config.frame_cls._context_manager

        # Remember the current context
        state._initial_publishing_context = context_manager.draft

        # Set the context
        context_manager.set_context(draft, published)

    return set_context
