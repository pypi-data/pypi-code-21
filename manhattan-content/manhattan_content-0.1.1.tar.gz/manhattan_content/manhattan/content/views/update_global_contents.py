"""
Generic update global contents asset chain.

This view updates contents with the `GlobalRegion` collection.
"""

import json
import re

from bs4 import BeautifulSoup
import flask
from manhattan.assets import Asset
from manhattan.assets.transforms.base import BaseTransform
from manhattan.assets.transforms.images import Fit
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import GlobalRegion
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories
from mongoframes import Q

__all__ = ['update_global_contents_chains']


# Define the chains
update_global_contents_chains = ChainMgr()

update_global_contents_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_contents',
    'get_global_regions',
    'sync_images',
    'update_contents',
    'render_json'
])


# Define the links

update_global_contents_chains.set_link(manage_factories.config())
update_global_contents_chains.set_link(manage_factories.authenticate())
update_global_contents_chains.set_link(factories.get_contents())

@update_global_contents_chains.link
def get_global_regions(state):
    """
    Get the global regions that will be update based on the contents.

    This link adds the `global_regions` key to the state, which contains a
    dictionary of global regions to apply the update to, e.g
    `{region_name: instance}`.

    NOTE: If the contents contains a region name that doesn't exist a new
    region will be created.
    """

    # Build the table of global regions
    global_regions = {}
    for region_name, content in state.contents.items():

        # Attempt to find the named global region
        global_region = GlobalRegion.one(Q.name == region_name)

        # If there's no existing region with that name then add one
        if not global_region:
            global_region = GlobalRegion(name=region_name)
            global_region.logged_insert(state.manage_user)

        global_regions[region_name] = global_region

    # Add the global regions to the state
    state.global_regions = global_regions

@update_global_contents_chains.link
def sync_images(state):
    """
    Temporary and permenant images inserted into the contents must be
    synchronized, by which we mean that temporary assets are converted to
    permenant assets and the content variation of the image is resized to
    match the width/height.

    This link adds the key `assets` to state which contains a dictionary of
    assets values for global regions, these are then used to update the global
    regions in the `update_contents` step.
    """
    asset_mgr = flask.current_app.asset_mgr

    # Take a copy of the assets for each global region we're updating
    state.assets = {}
    for region_name, content in state.contents.items():
        global_region = state.global_regions[region_name]
        state.assets[region_name] = global_region.assets.copy()

    # Get the variation name for content images
    config = flask.current_app.config
    variation_name = config.get('CONTENT_VARIATION_NAME', 'image')

    # Search the content for image tags with asset keys
    image_tags = []
    for region_name, content in state.contents.items():
        soup = BeautifulSoup(content, 'lxml')
        keyed_tags = soup.find_all(**{'data-mh-asset-key': True})
        for tag in keyed_tags:
            if tag.name == 'img':
                image_tags.append((region_name, tag))
            else:
                # Cater for image fixtures
                image_tag = tag.find('img')
                image_tag['data-mh-asset-key'] = tag['data-mh-asset-key']
                image_tags.append((region_name, image_tag))

    # Store and resize any images within the contents
    for image_tag in image_tags:
        region_name = image_tag[0]
        global_region = state.global_regions[region_name]
        tag = image_tag[1]

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

        elif asset_key in global_region.assets:
            # Existing image
            asset = Asset(global_region.assets[asset_key])

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
        state.assets[region_name][asset.key] = asset_json

        # Replace the existing image src within the content with the new one
        new_url = asset.variations[variation_name].url
        state.contents[region_name] = \
                state.contents[region_name].replace(url, new_url)

@update_global_contents_chains.link
def update_contents(state):
    """Update the contents of global regions within the contents"""
    for region_name, content in state.contents.items():
        state.global_regions[region_name].logged_update(
            state.manage_user,
            {'content': content, 'assets': state.assets[region_name]}
        )

@update_global_contents_chains.link
def render_json(state):
    """Render a JSON response for the successful saving of content"""
    return manage_utils.json_success()