"""
Generic add snippet chain.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import Snippet, SnippetType
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

__all__ = ['add_snippet_chains']


# Define the chains
add_snippet_chains = ChainMgr()

# POST
add_snippet_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'get_snippet_type',
    'add_snippet',
    'update_flow',
    'render_json'
])


# Define the links
add_snippet_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
add_snippet_chains.set_link(manage_factories.authenticate())
add_snippet_chains.set_link(manage_factories.get_document())
add_snippet_chains.set_link(factories.get_flow())
add_snippet_chains.set_link(factories.update_flow())

@add_snippet_chains.link
def get_snippet_type(state):
    """
    Get the type of snippet we'll be adding to the flow.

    This link adds `snippet_type` to the state.
    """

    # Get the snippet type Id requested
    snippet_type_id = flask.request.values.get('snippet_type', None)
    if not snippet_type_id:
        return manage_utils.json_fail('No `snippet_type` specified')

    # Get the available snippet types for the flow
    snippet_types = SnippetType.get_snippet_types([state.flow_id])

    # Make sure the given snippet type is available
    snippet_type = snippet_types.get(snippet_type_id, None)
    if not snippet_type:
        return manage_utils.json_fail('Snippet type not found')

    state.snippet_type = snippet_type

@add_snippet_chains.link
def add_snippet(state):
    """
    Add a snippet to the named flow.

    This link adds `snippet` to the state.
    """

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Create the new snippet
    snippet = Snippet(
        type=state.snippet_type.id,
        scope='local',
        local_settings=state.snippet_type.get_default_settings()
    )

    # Add the snippet to the flow
    state.flow.append(snippet)

    # Add the snippet to the state
    state.snippet = snippet

@add_snippet_chains.link
def render_json(state):
    """Render the new snippet as HTML and return it in a JSON response"""

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Render the snippet as HTML
    snippet_html = state.snippet.render(
        {state.manage_config.var_name: document}
    )

    return manage_utils.json_success({'html': snippet_html})
