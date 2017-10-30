"""
Generic revert document chain.

: `projection`
    The projection used when requesting the document from the database (defaults
    to None which means the detault projection for the frame class will be
    used).

"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.manage.views import (
    factories as manage_factories,
    utils as manage_utils
)
from manhattan.nav import Nav, NavItem

__all__ = ['revert_chains']


# Define the chains
revert_chains = ChainMgr()

# GET
revert_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'decorate',
    'render_template'
])

# POST
revert_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'revert_document',
    'redirect'
])


# Define the links
revert_chains.set_link(manage_factories.config(projection=None))
revert_chains.set_link(manage_factories.authenticate())
revert_chains.set_link(manage_factories.get_document())
revert_chains.set_link(manage_factories.render_template('revert.html'))
revert_chains.set_link(manage_factories.redirect('view', include_id=True))


@revert_chains.link
def decorate(state):
    """
    Add decor information to the state (see `manage_utils.base_decor` for
    further details on what information the `decor` dictionary consists of).

    This link adds a `decor` key to the state.
    """
    document = state[state.manage_config.var_name]
    state.decor = manage_utils.base_decor(
        state.manage_config,
        state.view_type
    )

    # Title
    state.decor['title'] = 'Revert ' + state.manage_config.titleize(document)

    # Breadcrumbs
    if Nav.exists(state.manage_config.get_endpoint('list')):
        state.decor['breadcrumbs'].add(
            manage_utils.create_breadcrumb(state.manage_config, 'list')
        )
    if Nav.exists(state.manage_config.get_endpoint('view')):
        state.decor['breadcrumbs'].add(
            manage_utils.create_breadcrumb(
                state.manage_config,
                'view',
                document
            )
        )
    state.decor['breadcrumbs'].add(NavItem('Revert'))

@revert_chains.link
def revert_document(state):
    """Revert the document"""

    # Get the document
    document = state[state.manage_config.var_name]

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Revert the document
    document.revert(state.manage_user)

    # Flash message that the document was published
    flask.flash('{document} reverted.'.format(document=document))
