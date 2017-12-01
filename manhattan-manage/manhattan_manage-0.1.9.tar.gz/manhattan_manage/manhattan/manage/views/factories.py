"""
Link factories for manhattan views.
"""


import bson
import os
import urllib

import flask
import inflection
from manhattan import secure
from manhattan.nav import Nav, NavItem
from manhattan.manage.views import utils

# Optional imports
try:
    from manhattan.assets import Asset
except ImportError as e:
    pass

__all__ = [
    'authenticate',
    'config',
    'decorate',
    'get_document',
    'init_form',
    'redirect',
    'render_template',
    'store_assets',
    'validate'
    ]


def authenticate(
        user_g_key='user',
        sign_in_endpoint='manage_users.sign_in',
        sign_out_endpoint='manage_users.sign_out'
        ):
    """
    Authenticate the caller has permission to call the view.

    This link adds a `user` key to the the state containing the currently signed
    in user.
    """

    def authenticate(state):
        # Get the signed in user
        state.manage_user = flask.g.get(user_g_key)

        # We're not allowed to access this view point so determine if that's
        # because we're not sign-in or because we don't have permission.
        if not state.manage_user:
            # We need to sign-in to view this endpoint

            # Forward the user to the sign-in page with the requested URL as the
            # `next` parameter.
            redirect_url = flask.url_for(
                sign_in_endpoint,
                next=secure.safe_redirect_url(
                    flask.request.url,
                    [flask.url_for(sign_out_endpoint)]
                    )
                )
            return flask.redirect(redirect_url)

        # Check if we're allowed to access this requested endpoint
        if not Nav.allowed(flask.request.endpoint, **flask.request.view_args):

            # We don't have permission to view this endpoint
            flask.abort(403, 'Permission denied')

    return authenticate

def config(**defaults):
    """
    Return a function will configure a view's state adding defaults where no
    existing value currently exists in the state.

    This function is designed to be included as the first link in a chain and
    to set the initial state so that chains can be configured on a per copy
    basis.
    """

    def config(state):
        # Apply defaults
        for key, value in defaults.items():

            # First check if a value is already set against the state
            if key in state:
                continue

            # If not then set the default
            state[key] = value

    return config

def decorate(view_type, title=None, last_breadcrumb=None, tabs=None):
    """
    Return a function that will add decor information to the state for the
    named view.
    """

    def decorate(state):
        document = state.get(state.manage_config.var_name)
        state.decor = utils.base_decor(state.manage_config, state.view_type)

        # Title
        if document:
            state.decor['title'] = '{action} {target}'.format(
                action=inflection.humanize(view_type),
                target=state.manage_config.titleize(document)
            )
        else:
            state.decor['title'] = inflection.humanize(view_type)

        # Breadcrumbs
        if Nav.exists(state.manage_config.get_endpoint('list')):
            state.decor['breadcrumbs'].add(
                utils.create_breadcrumb(state.manage_config, 'list')
            )
        if Nav.exists(state.manage_config.get_endpoint('view')) and document:
            state.decor['breadcrumbs'].add(
                utils.create_breadcrumb(state.manage_config, 'view', document)
            )
        state.decor['breadcrumbs'].add(NavItem('Update'))

    return decorate

def get_document(projection=None):
    """
    Return a function that will attempt to retreive a document from the
    database by `_id` using the `var_name` named parameter in the request.

    This link adds a `{state.manage_config.var_name}` key to the the state
    containing the document retreived.

    Optionally a projection to use when getting the document can be specified,
    if no projection is specified then the function will look for a projection
    against the state (e.g state.projection).
    """

    def get_document(state):
        # Get the Id of the document passed in the request
        document_id = flask.request.values.get(state.manage_config.var_name)

        # Attempt to convert the Id to the required type
        try:
            document_id = bson.objectid.ObjectId(document_id)
        except bson.errors.InvalidId:
            flask.abort(404)

        # Attempt to retrieve the document
        by_id_kw = {}
        if projection or state.projection:
            by_id_kw['projection'] = projection or state.projection

        document = state.manage_config.frame_cls.by_id(
            document_id,
            **by_id_kw
        )

        if not document:
            flask.abort(404)

        # Set the document against the state
        state[state.manage_config.var_name] = document

    return get_document

def init_form(populate_on=None):
    """
    Return a function that will initialize a form for the named generic view
    (e.g list, add, update, etc.) or the given form class.

    This link adds a `form` key to the the state containing the initialized
    form.
    """

    # If populate_on is not specified then we default to `POST`
    if populate_on is None:
        populate_on = ['POST']

    def init_form(state):
        # Get the form class
        assert state.form_cls, 'No form class `form_cls` defined'

        # Initialize the form
        form_data = None
        if flask.request.method in populate_on:
            if flask.request.method in ['POST', 'PUT']:
                form_data = flask.request.form
            else:
                form_data = flask.request.args

        # If a document is assign to the state then this is sent as the first
        # argument when initializing the form.
        obj = None
        if state.manage_config.var_name in state:
            obj = state[state.manage_config.var_name]

        # Initialize the form
        state.form = state.form_cls(form_data, obj=obj)

    return init_form

def redirect(endpoint, include_id=False):
    """
    Return a function that will trigger a redirect to the given endpoint.

    Optionally an Id for the current document in the state can be added to the
    URL, e.g `url_for('view.user', user=user._id)` by passing `include_id` as
    True.
    """

    def redirect(state):
        # Build the URL arguments
        url_args = {}
        if include_id:
            url_args[state.manage_config.var_name] = \
                    state[state.manage_config.var_name]._id

        # Get the URL for the endpoint
        prefix = state.manage_config.endpoint_prefix
        if state.manage_config.endpoint_prefix:
            url = flask.url_for('.' + prefix + endpoint, **url_args)
        else:
            url = flask.url_for('.' + endpoint, **url_args)

        # Return the redirect response
        return flask.redirect(url)

    return redirect

def render_template(template_path):
    """
    Return a function that will render the named template. The state object is
    used as template arguments.
    """

    def render_template(state):
        # Build the template filepath
        full_template_path = os.path.join(
            state.manage_config.template_path,
            template_path
        )

        # Render the template
        return flask.render_template(full_template_path, **state)

    return render_template

def store_assets():
    """
    Return a function that will convert temporary assets to permenant assets.
    """

    def store_assets(state):

        # Check that the app supports an asset manager, if not then there's
        # nothing to do.
        if not hasattr(flask.current_app, 'asset_mgr'):
            return
        asset_mgr = flask.current_app.asset_mgr

        # Get the document being added or updated
        document = state[state.manage_config.var_name]

        # Find any values against the document which are temporary assets
        update_fields = []
        for field in document.get_fields():
            value = document.get(field)

            # Ignore any value that's not a temporary asset
            if not (isinstance(value, Asset) and value.temporary):
                continue

            # Store the asset permenantly
            flask.current_app.asset_mgr.store(value)

            # Check if any variations are defined for the field
            if hasattr(state.manage_config, field + '_variations'):
                variations = getattr(state.manage_config, field + '_variations')

                # Store variations for the asset
                asset_mgr.generate_variations(value, variations)

            # Flag the field requires updating against the database
            update_fields.append(field)

        if update_fields:
            document.update(*update_fields)

    return store_assets

def validate(error_msg='Please review your submission'):
    """
    Return a function that will call validate against `state.form`. If the form
    is valid the function will return `True` or `False` if not.

    Optionally an `error_msg` can be passed, if the form fails to validate this
    will be flashed to the user.
    """

    def validate(state):
        assert state.form, 'No form to validate against'

        if state.form.validate():
            return True

        flask.flash(error_msg, 'error')
        return False

    return validate
