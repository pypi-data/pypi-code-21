"""
Generic change snippet scope chain.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import GlobalSnippet
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories
from mongoframes import Q

__all__ = ['change_snippet_scope_chains']


# Define the chains
change_snippet_scope_chains = ChainMgr()

# POST
change_snippet_scope_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'get_snippet',
    'change_snippet_scope',
    'update_flow',
    'render_json'
])


# Define the links
change_snippet_scope_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
change_snippet_scope_chains.set_link(manage_factories.authenticate())
change_snippet_scope_chains.set_link(manage_factories.get_document())
change_snippet_scope_chains.set_link(factories.get_flow())
change_snippet_scope_chains.set_link(factories.get_snippet())
change_snippet_scope_chains.set_link(factories.update_flow())

@change_snippet_scope_chains.link
def change_snippet_scope(state):
    """Change the scope of a snippet"""

    # Get the scope we're changing to
    scope = flask.request.values.get('scope', None)
    if scope not in ['global', 'local']:
        return manage_utils.json_fail('`scope` must be local or global')

    # Check the scope needs changing
    if state.snippet.scope == scope:
        return

    # Change the scope of the snippet
    if scope == 'local':
        # Global > Local

        # Store settings and content slocally
        settings = state.snippet.settings
        contents = state.snippet.contents
        state.snippet.scope = 'local'
        state.snippet.local_settings = settings
        state.snippet.local_contents = contents

        # Remove the global Id from the snippet
        del state.snippet._document['global_id']

    else:
        # Local > Global

        # Get the label to use for global snippet
        label = flask.request.values.get('label', None).strip()
        if not label:
            return manage_utils.json_fail(
                'No `label` specified',
                {'label': 'This field is required'}
                )

        # Check the label is unique
        if GlobalSnippet.count(Q.label == label):
            return manage_utils.json_fail(
                'Not a valid label',
                {'label': 'Labels must be unqiue'}
                )

        # Create the global snippet
        global_snippet = GlobalSnippet(
            type=state.snippet.type,
            visible=True,
            settings=state.snippet.local_settings,
            contents=state.snippet.contents,
            label=label
        )
        global_snippet.insert()

        # Update the snippet so it references the new global snippet
        state.snippet.scope = 'global'
        state.snippet.local_settings = {}
        state.snippet.local_contents = {}
        state.snippet.global_id = global_snippet._id

@change_snippet_scope_chains.link
def render_json(state):
    """
    Render a JSON response for the successful change of the snippet's scope.
    """
    return manage_utils.json_success()
