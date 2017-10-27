"""
Generic publish document chain.

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

from manhattan.publishing.exceptions import PublishingError

__all__ = ['publish_chains']


# Define the chains
publish_chains = ChainMgr()

# GET
publish_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'decorate',
    'render_template'
])

# POST
publish_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'publish_document',
    'redirect'
])


# Define the links
publish_chains.set_link(manage_factories.config(projection=None))
publish_chains.set_link(manage_factories.authenticate())
publish_chains.set_link(manage_factories.get_document())
publish_chains.set_link(manage_factories.render_template('publish.html'))
publish_chains.set_link(manage_factories.redirect('view', include_id=True))


@publish_chains.link
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
    state.decor['title'] = 'Publish ' + state.manage_config.titleize(document)

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
    state.decor['breadcrumbs'].add(NavItem('Publish'))

@publish_chains.link
def publish_document(state):
    """Publish the document"""

    # Get the document
    document = state[state.manage_config.var_name]

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Publish the document
    try:
        document.publish(state.manage_user)
    except PublishingError as e:
        return flask.flash('Unable to publish: {0}'.format(e), 'error')

    # Flash message that the document was published
    flask.flash('{document} published.'.format(document=document))
