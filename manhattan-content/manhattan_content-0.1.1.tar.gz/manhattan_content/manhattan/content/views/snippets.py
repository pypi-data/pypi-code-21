"""
Generic get snippets chain.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import Snippet
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

__all__ = ['snippets_chains']


# Define the chains
snippets_chains = ChainMgr()

# GET
snippets_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'render_json'
    ])


# Define the links
snippets_chains.set_link(manage_factories.config(content_flows_field='flows'))
snippets_chains.set_link(manage_factories.authenticate())
snippets_chains.set_link(manage_factories.get_document())
snippets_chains.set_link(factories.get_flow())

@snippets_chains.link
def render_json(state):
    """Render and return the snippets in JSON format"""

    # Build the payload
    payload = {'snippets': [s.to_json_type() for s in state.flow]}

    return manage_utils.json_success(payload)
