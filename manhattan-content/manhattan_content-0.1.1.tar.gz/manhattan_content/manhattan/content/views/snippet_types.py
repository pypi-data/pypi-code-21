"""
Generic get snippet types chain.
"""

from operator import attrgetter

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import SnippetType
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

__all__ = ['snippet_types_chains']


# Define the chains
snippet_types_chains = ChainMgr()

# GET
snippet_types_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_snippet_types',
    'render_json'
    ])


# Define the links
snippet_types_chains.set_link(manage_factories.config())
snippet_types_chains.set_link(manage_factories.authenticate())

@snippet_types_chains.link
def get_snippet_types(state):
    """
    Get a list of snippet types available to the given content flow.

    This link adds a `snippet_types` list to the state.
    """

    # Get the content flow Id requested
    flow_id = flask.request.args.get('flow', None)
    if not flow_id:
        return manage_utils.json_fail('No `flow` specified')

    # Get the available snippet types for the flow
    snippet_types = list(SnippetType.get_snippet_types([flow_id]).values())

    # Order the snippet types by their label
    snippet_types.sort(key=attrgetter('label'))

    state.snippet_types = snippet_types

@snippet_types_chains.link
def render_json(state):
    """Render and return the snippet types in JSON format"""

    # Build the payload
    payload = {'snippet_types': [s.to_json_type() for s in state.snippet_types]}

    return manage_utils.json_success(payload)
