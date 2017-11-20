"""
Generic delete snippet chain.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

__all__ = ['delete_snippet_chains']


# Define the chains
delete_snippet_chains = ChainMgr()

# POST
delete_snippet_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'get_snippet',
    'delete_snippet',
    'update_flow',
    'render_json'
])


# Define the links
delete_snippet_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
delete_snippet_chains.set_link(manage_factories.authenticate())
delete_snippet_chains.set_link(manage_factories.get_document())
delete_snippet_chains.set_link(factories.get_flow())
delete_snippet_chains.set_link(factories.get_snippet())
delete_snippet_chains.set_link(factories.update_flow())

@delete_snippet_chains.link
def delete_snippet(state):
    """Delete a snippet from a flow"""
    state.flow = [s for s in state.flow if s['id'] != state.snippet.id]

@delete_snippet_chains.link
def render_json(state):
    """Render a JSON response for the successful deletion of the snippet"""
    return manage_utils.json_success()
