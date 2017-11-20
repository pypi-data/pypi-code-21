from collections import namedtuple

from .add_snippet import add_snippet_chains
from .add_global_snippet import add_global_snippet_chains
from .change_snippet_scope import change_snippet_scope_chains
from .delete_snippet import delete_snippet_chains
from .global_snippets import global_snippets_chains
from .order_snippets import order_snippets_chains
from .snippet_types import snippet_types_chains
from .snippets import snippets_chains
from .update_contents import update_contents_chains
from .update_flow_contents import update_flow_contents_chains
from .update_global_contents import update_global_contents_chains
from .update_snippet_settings import update_snippet_settings_chains

__all__ = ['generic']


# We name space generic views using a named tuple to provide a slightly nicer
# way to access them, e.g:
#
#     from manhattan.content.views import generic
#
#     view = generic.snippets
#
# And to make it easy to iterate through the list of generic views to make
# changes, e.g:
#
#     def authenticate(state):
#         """A custom authenticator for my site"""
#
#         ...
#
#     for view in generic:
#         view.set_link(authenticate)

# Define the named tuple (preventing the list of generic views being altered)
Generic = namedtuple(
    'Generic',
    [
        'add_snippet',
        'add_global_snippet',
        'change_snippet_scope',
        'delete_snippet',
        'global_snippets',
        'order_snippets',
        'snippet_types',
        'snippets',
        'update_contents',
        'update_flow_contents',
        'update_global_contents',
        'update_snippet_settings'
    ])

# Create an instance of Generic containing all the generic views
generic = Generic(
    add_snippet=add_snippet_chains,
    add_global_snippet=add_global_snippet_chains,
    change_snippet_scope=change_snippet_scope_chains,
    delete_snippet=delete_snippet_chains,
    global_snippets=global_snippets_chains,
    order_snippets=order_snippets_chains,
    snippet_types=snippet_types_chains,
    snippets=snippets_chains,
    update_contents=update_contents_chains,
    update_flow_contents=update_flow_contents_chains,
    update_global_contents=update_global_contents,
    update_snippet_settings=update_snippet_settings_chains
    )