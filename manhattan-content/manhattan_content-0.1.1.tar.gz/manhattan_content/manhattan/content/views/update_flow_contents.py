"""
Generic update contents chain for content flows.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import json
import re

from bs4 import BeautifulSoup
import flask
from manhattan.assets import Asset
from manhattan.assets.transforms.base import BaseTransform
from manhattan.assets.transforms.images import Fit
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import Snippet
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

__all__ = ['update_flow_contents_chains']


# Define the chains
update_flow_contents_chains = ChainMgr()

update_flow_contents_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flows',
    'get_contents',
    'sync_images',
    'update_contents',
    'update_flows',
    'render_json'
])


# Define the links

update_flow_contents_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
update_flow_contents_chains.set_link(manage_factories.authenticate())
update_flow_contents_chains.set_link(manage_factories.get_document())
update_flow_contents_chains.set_link(factories.get_contents())

@update_flow_contents_chains.link
def get_flows(state):
    """
    Get the flows that we're applying updates to.

    This link adds `flows` and `original_flows` keys to the state containing the
    flows that are to be updated.
    """

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Get the flows we'll be updating
    state.flows = (document.get(state.content_flows_field) or {}).copy()
    state.original_flows = state.flows.copy()

    # Ensure all snippets in all flows are `Snippet` instances
    for flow_id, flow in state.flows.items():
        for i, snippet in enumerate(flow):
            if not isinstance(snippet, Snippet):
                flow[i] = Snippet(snippet)

@update_flow_contents_chains.link
def sync_images(state):
    """
    Temporary and permenant images inserted into the contents must be
    synchronized, by which we mean that temporary assets are converted to
    permenant assets and the content variation of the image is resized to
    match the width/height.
    """
    asset_mgr = flask.current_app.asset_mgr

    # Get the variation name for content images
    config = flask.current_app.config
    variation_name = config.get('CONTENT_VARIATION_NAME', 'image')

    # Build a table of snippet Ids within all flows so that we can quickly look
    # up the related contents dictionary.
    snippet_table = {}
    for flow_id, flow in state.flows.items():
        for snippet in flow:
            snippet_table[snippet.id] = snippet

    # Search the content for image tags with asset keys
    image_tags = []
    for snippet, snippet_contents in state.contents.items():
        for region, content in snippet_contents.items():
            soup = BeautifulSoup(content, 'lxml')
            keyed_tags = soup.find_all(**{'data-mh-asset-key': True})
            for tag in keyed_tags:
                if tag.name == 'img':
                    image_tags.append((snippet, region, tag))
                else:
                    # Cater for image fixtures
                    image_tag = tag.find('img')
                    image_tag['data-mh-asset-key'] = tag['data-mh-asset-key']
                    image_tags.append((snippet, region, image_tag))

    for image_tag in image_tags:
        snippet = snippet_table[image_tag[0]]
        region = image_tag[1]
        tag = image_tag[2]

        # Ensure the snippet's contents contains the special `__assets__` key
        if not snippet.local_contents.get('__assets__'):
            snippet.local_contents['__assets__'] = {}

        # Extract the asset key, width and height from the image
        asset_key = tag['data-mh-asset-key']
        url = tag['src']
        width = tag.attrs.get('width', '')

        # If there's no associated asset key then ignore the image
        if not asset_key:
            continue

        # If a valid width is specified create a resize transform
        resize_transform = None
        if width.isdigit() and int(width) > 0:
            # Create a resize transform that will be used to set the size of the
            # image within the content.
            width = int(width)

            # HACK: We set the height to an arbitrary high value so we can
            # simplify the problem to just width.
            #
            # ~ Anthony Blackshaw <ant@getme.co.uk>, 31 August 2017
            #
            resize_transform = Fit(width, 99999)

        else:
            # No valid width so set the width to None
            width = None

        # If the image asset is temporary then we need to store a permenant
        # copy of it.
        asset = None
        if asset_mgr.get_temporary_by_key(asset_key):
            # New image
            asset = asset_mgr.get_temporary_by_key(asset_key)

            # Store the asset permenantly
            flask.current_app.asset_mgr.store(asset)

        elif asset_key in snippet.contents['__assets__']:
            # Existing image
            asset = Asset(snippet.contents['__assets__'][asset_key])

            # If this is a permenant asset check if we need to resize it
            variation = asset.variations.get(variation_name)

            if variation:
                size = variation['core_meta']['image']['size']
                if width == size[0]:
                    continue

        else:
            # Asset not found so continue
            continue

        # Create to match the base transform
        transforms = [
            BaseTransform.from_json_type(t) for t in asset.base_transforms]

        # If there's a width specified then a resize will be required
        if width:
            transforms += [resize_transform]

        asset_mgr.generate_variations(asset, {variation_name: transforms})

        if width:
            asset.variations[variation_name].local_transforms = [
                resize_transform.to_json_type()
            ]

        # Store the updated asset against the snippet's contents
        asset_json = asset.to_json_type()
        if snippet.scope == 'local':
            snippet.local_contents['__assets__'][asset.key] = asset_json
        else:
            global_snippet = snippet.global_snippet
            global_snippet.contents['__assets__'][asset.key] = asset_json

        # Replace the existing image src within the content with the new one
        new_url = asset.variations[variation_name].url
        state.contents[snippet.id][region] = \
                state.contents[snippet.id][region].replace(url, new_url)

@update_flow_contents_chains.link
def update_contents(state):
    """Update the contents of snippets with the flows"""

    # Apply the changes
    for flow_id, flow in state.flows.items():
        for snippet in flow:
            if snippet.id not in state.contents:
                continue

            if snippet.scope == 'local':
                # Apply changes to this snippet
                snippet.local_contents.update(state.contents[snippet.id])

            elif snippet.scope == 'global':
                # Apply changes to the global snippet this snippet references
                global_snippet = snippet.global_snippet

                # Update the contents
                global_contents = global_snippet.contents.copy()
                global_contents.update(state.contents[snippet.id])

                # Update the global snippet
                global_snippet.logged_update(
                    state.manage_user,
                    {'contents': global_contents}
                )

                # Clear global snippet cache from the snippet
                state.snippet._global_snippet_cache = None

@update_flow_contents_chains.link
def update_flows(state):
    """Perform a logged or straight update of flows within the document"""

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Check to see if the frame class supports `logged_update`s
    if hasattr(state.manage_config.frame_cls, 'logged_update'):
        # Logged update
        document.logged_update(
            state.manage_user,
            {state.content_flows_field: state.flows}
        )

    else:
        # Straight update (no logging)
        setattr(document, state.content_flows_field, state.flows)
        document.update(state.content_flows_field)

@update_flow_contents_chains.link
def render_json(state):
    """Render a JSON response for the successful saving of content"""
    return manage_utils.json_success()