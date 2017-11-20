"""
Generic add global snippet chain.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import bson

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import GlobalSnippet, Snippet, SnippetType
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories
from mongoframes import And, Q

__all__ = ['add_global_snippet_chains']


# Define the chains
add_global_snippet_chains = ChainMgr()

# POST
add_global_snippet_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'get_global_snippet',
    'add_snippet',
    'update_flow',
    'render_json'
])


# Define the links
add_global_snippet_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
add_global_snippet_chains.set_link(manage_factories.authenticate())
add_global_snippet_chains.set_link(manage_factories.get_document())
add_global_snippet_chains.set_link(factories.get_flow())
add_global_snippet_chains.set_link(factories.update_flow())

@add_global_snippet_chains.link
def get_global_snippet(state):
    """
    Get the global snippet we'll be adding to the flow.

    This link adds `global_snippet` to the state.
    """

    # Get the snippet types supported by the flow
    snippet_types = SnippetType.get_snippet_types([state.flow_id])

    # Get the global snippet Id
    global_id = flask.request.values.get('global_snippet', None)
    if not global_id:
        return manage_utils.json_fail('No `global_snippet` specified')

    try:
        global_id = bson.objectid.ObjectId(global_id)
    except bson.errors.InvalidId:
        return manage_utils.json_fail('`global_snippet` is not a valid Id')

    # Get the global snippet
    global_snippet = GlobalSnippet.one(
        And(Q._id == global_id, Q.visible == True)
    )
    if not global_snippet:
        return manage_utils.json_fail('Global snippet not found')

    state.global_snippet = global_snippet

@add_global_snippet_chains.link
def add_snippet(state):
    """
    Add a global snippet to the named flow.

    This link adds `snippet` to the state.
    """

    # Create the new snippet
    snippet = Snippet(
        type=state.global_snippet.type,
        scope='global',
        global_id=state.global_snippet._id
    )

    # Add the snippet to the flow
    state.flow.append(snippet)

    # Add the snippet to the state
    state.snippet = snippet

@add_global_snippet_chains.link
def render_json(state):
    """Render the new snippet as HTML and return it in a JSON response"""

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Render the snippet as HTML
    snippet_html = state.snippet.render(
        {state.manage_config.var_name: document}
    )

    return manage_utils.json_success({'html': snippet_html})
