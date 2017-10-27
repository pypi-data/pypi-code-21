"""
Generic get global snippets chain.
"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import GlobalSnippet, SnippetType
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories
from mongoframes import ASC, In, Q

__all__ = ['global_snippets_chains']


# Define the chains
global_snippets_chains = ChainMgr()

# GET
global_snippets_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_global_snippets',
    'render_json'
    ])


# Define the links
global_snippets_chains.set_link(manage_factories.config())
global_snippets_chains.set_link(manage_factories.authenticate())

@global_snippets_chains.link
def get_global_snippets(state):
    """
    Get a list of global snippets available to the flow.

    This link adds a `global_snippets` list to the state.
    """

    # Get the content flow Id requested
    flow_id = flask.request.args.get('flow', None)
    if not flow_id:
        return manage_utils.json_fail('No `flow` specified')

    # Get a list of types supported by the flow
    snippet_types = SnippetType.get_snippet_types([flow_id])
    type_ids = [t.id for t in snippet_types.values()]

    # Get a list of global snippets available to the flow
    state.global_snippets = GlobalSnippet.many(
        In(Q.type, type_ids),
        sort=[('label', ASC)]
    )

@global_snippets_chains.link
def render_json(state):
    """
    Render and return the global snippet in JSON format.
    """

    # Build the payload
    payload = {
        'snippets': [
            s.to_snippet().to_json_type() for s in state.global_snippets
        ]
    }

    return manage_utils.json_success(payload)