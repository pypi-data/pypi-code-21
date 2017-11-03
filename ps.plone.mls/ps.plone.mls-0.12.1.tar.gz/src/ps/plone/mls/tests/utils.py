# -*- coding: utf-8 -*-
"""Testing utilities."""

# python imports
from mls.apiclient import testing
from mls.apiclient.tests import utils
import os


def _register(endpoint, content=None, fixture=None, params=None):
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'fixtures',
    )
    return testing._register(
        endpoint,
        content=content,
        path=path,
        fixture=fixture,
        params=params,
    )


def setup_plone_mls_fixtures():
    """Setup the test fixtures for integration tests."""
    utils.setup_listing_api_fixtures()
    utils.setup_fixtures()

    # Register Plone specific development endpoints
    _register(
        'developments',
        params=dict(
            {
                'fields': ''.join([
                    'id,title,description,logo,location,lot_size,'
                    'location_type,number_of_listings,number_of_groups'
                ]),
                'limit': 5,
                'offset': 0,
            },
            **testing.BASE_PARAMS),
        fixture='developments.json',
    )
    _register(
        'developments',
        params=dict(
            {
                'fields': ''.join([
                    'id,title,description,logo,location,lot_size,'
                    'location_type,number_of_listings,number_of_groups,'
                    'banner_image'
                ]),
                'reverse': False,
                'modify_url': True,
                'limit': 5,
                'offset': 0,
            },
            **testing.BASE_PARAMS),
        fixture='developments_banner.json',
    )
