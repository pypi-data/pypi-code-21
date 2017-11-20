"""
Generic update snippet settings chain.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.content.views import factories
from manhattan.forms import BaseForm, fields, validators
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

__all__ = ['update_snippet_settings_chains']


# Define the chains
update_snippet_settings_chains = ChainMgr()

# GET
update_snippet_settings_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'get_snippet',
    'init_form',
    'convert_form_to_json_type',
    'render_get_json'
])

# POST
update_snippet_settings_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flow',
    'get_snippet',
    'init_form',
    'validate',
    'build_form_data',
    'update_snippet_settings',
    'update_flow',
    'render_post_json'
])


# Define the links

update_snippet_settings_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
update_snippet_settings_chains.set_link(manage_factories.authenticate())
update_snippet_settings_chains.set_link(manage_factories.get_document())
update_snippet_settings_chains.set_link(factories.get_flow())
update_snippet_settings_chains.set_link(factories.get_snippet())
update_snippet_settings_chains.set_link(factories.update_flow())

@update_snippet_settings_chains.link
def init_form(state):
    """
    Initialize a form for the settings of snippet being updated, the form is
    aquired from the snippet's snippet type class.

    This link adds a `form` key to the the state containing the initialized
    form.
    """

    # Check the snippet's type has a settings form
    form = None
    form_cls = state.snippet.type_cls.get_settings_form()
    if form_cls:

        # Initialize the form
        form_data = None
        if flask.request.method == 'POST':
            form_data = flask.request.form

        form = form_cls(form_data, **state.snippet.settings)

    # Add the form to the state
    state.form = form

@update_snippet_settings_chains.link
def validate(state):
    """
    Validate data POSTed to the view against `state.form`. If the form is valid
    the function will return `True` or `False` if not.
    """

    # Only attempt to validate if there's a form
    if not state.form:
        return

    # Validate the form
    if not state.form.validate():
        return manage_utils.json_fail(
            'Invalid form submission',
            state.form.errors
        )

@update_snippet_settings_chains.link
def build_form_data(state):
    """
    Generate the form data that will be used to update the snippet's settings.

    This link adds a `form_data` key to the the state.
    """

    state.form_data = {}
    if state.form:
        state.form_data = state.form.data

@update_snippet_settings_chains.link
def update_snippet_settings(state):
    """Update the snippet's settings"""

    if state.snippet.scope == 'local':
        # Apply changes to this snippet
        state.snippet.local_settings = state.form_data

    elif state.snippet.scope == 'global':
        # Apply changes to the global snippet this snippet references
        global_snippet = state.snippet.global_snippet

        # Update the global snippet
        global_snippet.logged_update(
            state.manage_user,
            {'settings': state.form_data}
        )

        # Clear global snippet cache from the snippet
        state.snippet._global_snippet_cache = None

@update_snippet_settings_chains.link
def convert_form_to_json_type(state):
    """
    Convert the settings form into to a list of fields represented as JSON
    safe data.

    ContentFlow supports boolean, select/options and text entry fields and so
    fields which can't be directly converted default to text entry.

    This link adds a `fields` key to the state containing the JSON type
    representation of the form fields.
    """

    # Field class to type map
    field_types = {
        fields.BooleanField: 'boolean',
        fields.DocumentSelectField: 'select',
        fields.SelectField: 'select'
    }

    # Serialize the form fields in to JSON safe data types
    form_fields = []
    if state.form:
        for field in state.form:

            # Get the initial value of the field
            value = field.default
            if field.name in state.snippet.settings:
                value = field.data

            # Build the base field data
            field_json = {
                'name': field.name,
                'label': field.label.text,
                'type': field_types.get(field.__class__, 'text'),
                'required': field.flags.required,
                'value': value
            }

            # Cater for different field types
            if isinstance(field, fields.SelectField):
                field_json['choices'] = field.choices

            form_fields.append(field_json)

    state.fields = form_fields

@update_snippet_settings_chains.link
def render_get_json(state):
    """Render a JSON representation of the snippets settings form"""

    return manage_utils.json_success({'fields': state.fields})

@update_snippet_settings_chains.link
def render_post_json(state):
    """
    Render a JSON response for the successful update of the snippet's
    settings.
    """

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Render the snippet as HTML
    snippet_html = state.snippet.render(
        {state.manage_config.var_name: document}
    )

    return manage_utils.json_success({'html': snippet_html})