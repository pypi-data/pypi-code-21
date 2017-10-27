"""
Generic order snippets chain.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import flask
import json
from manhattan.chains import Chain, ChainMgr
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

__all__ = ['order_snippets_chains']


# Define the chains
order_snippets_chains = ChainMgr()

# POST
order_snippets_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'order_snippets',
    'update_flow',
    'render_json'
])


# Define the links
order_snippets_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
order_snippets_chains.set_link(manage_factories.authenticate())
order_snippets_chains.set_link(manage_factories.get_document())
order_snippets_chains.set_link(factories.get_flow())
order_snippets_chains.set_link(factories.update_flow())

@order_snippets_chains.link
def order_snippets(state):
    """Order the snippets in a flow"""

    # Get the snippet Ids to use to set the order
    snippet_ids = flask.request.values.get('snippets', None)
    if not snippet_ids:
        return manage_utils.json_fail('No `snippets` specified')

    # Attempt to convert the snippet Ids string to a list
    try:
        snippet_ids = json.loads(snippet_ids)
    except ValueError:
        return manage_utils.json_fail('`snippets` is not valid JSON')

    # Build a look up table for snippets within the flow
    snippets = {s.id: s for s in state.flow}

    # Order the snippets
    ordered_flow = []
    for snippet_id in snippet_ids:
        if snippet_id in snippets:
            ordered_flow.append(snippets[snippet_id])

    if len(ordered_flow) != len(state.original_flow):
        return manage_utils.json_fail('Snippet Ids do not match the flow')

    state.flow = ordered_flow

@order_snippets_chains.link
def render_json(state):
    """Render a JSON response for the successful ordering of the snippets"""
    return manage_utils.json_success()
