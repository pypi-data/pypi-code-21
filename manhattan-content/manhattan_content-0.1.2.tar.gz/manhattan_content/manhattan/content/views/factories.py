"""
Link factories for content views.
"""

import json

import flask
from manhattan.content.snippets import Snippet
from manhattan.manage.views import utils as manage_utils
import re

__all__ = [
    'get_contents',
    'get_flow',
    'get_snippet',
    'update_flow'
    ]


def get_contents():
    """
    Return a function that will retreive and deserialize a dictionary of
    content that will be used to update a document (see `update_contents.py`,
    `update_flow_contents.py` and `update_global_contents`).

    This link adds the `contents` key to the state, which contains a dictionary
    of content to apply in the update.
    """

    def get_contents(state):

        # Get the contents we need to update the flows with
        try:
            state.contents = json.loads(
                flask.request.values.get('contents', '{}')
            )
        except ValueError:
            return manage_utils.json_fail('`contents` is not valid JSON')

    return get_contents

def get_flow():
    """
    Return a function to look up a content flow based on the `flow` request
    parameter and add it to the state.

    This link adds `flow` and `flow_id` and `original_flow` to the state. The
    original flow value is used for comparison when making logged updates are
    made.
    """

    def get_flow(state):

        # Get the document were holding the content flow
        document = state[state.manage_config.var_name]

        # Get the content flow Id requested
        flow_id = flask.request.values.get('flow', None)
        if not flow_id:
            return manage_utils.json_fail('No `flow` specified')

        # Ensure there's a table to get/set content flows against
        assert state.content_flows_field, 'No `content_flows_field` configured'
        flows = document.get(state.content_flows_field) or {}
        setattr(document, state.content_flows_field, flows)

        # Ensure all snippets are converted to instances of `Snippet`
        flow = flows.get(flow_id, [])
        for i, snippet in enumerate(flow):
            if not isinstance(snippet, Snippet):
                snippet = Snippet(snippet)
            flow[i] = snippet

        # Add flow and flow Id to the state
        state.original_flow = flow.copy()
        state.flow = flow.copy()
        state.flow_id = flow_id

    return get_flow

def get_snippet():
    """
    Return a function to find a snippet in a flow and add it to the state.

    This link adds `snippet` and to the state, it expects the state to contain
    the `flow` attribute.
    """

    def get_snippet(state):

        # Get the snippet Id to remove
        snippet_id = flask.request.values.get('snippet', None)
        if not snippet_id:
            return manage_utils.json_fail('No `snippet` specified')

        # Attempt to find the snippet
        snippet = None
        for s in state.flow:
            if s['id'] == snippet_id:
                snippet = s
                break

        # Check that the snippet was found
        if not snippet:
            return manage_utils.json_fail('Snippet not found')

        # Add the snippet to the state
        state.snippet = snippet

    return get_snippet

def update_flow():
    """
    Return a function to perform a logged or straight update of the flows field
    within a document for an individual flow.
    """

    def update_flow(state):

        # Get the document we're add the snippet to
        document = state[state.manage_config.var_name]

        # Update the flow within the document
        document[state.content_flows_field][state.flow_id] = state.flow

        # Check to see if the frame class supports `logged_update`s
        if hasattr(state.manage_config.frame_cls, 'logged_update'):

            # Timestamp
            document.__class__.timestamp_update(document, [document])

            # Update the document
            document.update('modified', state.content_flows_field)

            # Create an entry and perform a diff
            entry = document.__class__._change_log_cls({
                'type': 'UPDATED',
                'documents': [document],
                'user': state.manage_user
                })
            entry.add_diff(
                {state.content_flows_field: state.original_flow},
                {state.content_flows_field: state.flow}
            )

            # Log any differences
            if not entry.is_diff:
                entry.insert()

        else:
            # Straight update (no logging)
            document.update(state.content_flows_field)

    return update_flow