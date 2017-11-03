# -*- coding: utf-8 -*-
"""Show Listings for developments."""

# python imports
from mls.apiclient import exceptions

# zope imports
from Products.Five import BrowserView
from plone.memoize.view import memoize
from plone.mls.core.navigation import ListingBatch
from plone.mls.listing.browser.interfaces import IBaseListingItems
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.traversing.browser.absoluteurl import absoluteURL

# local imports
from ps.plone.mls import (
    api,
    config,
    logger,
)
from ps.plone.mls.interfaces import IDevelopmentListings


@implementer(IBaseListingItems, IDevelopmentListings)
class DevelopmentListings(BrowserView):
    """Show listings for a specific development."""

    _listings = None
    _batching = None
    limit = None
    item = None

    def __init__(self, context, request):
        super(DevelopmentListings, self).__init__(context, request)
        self.update()

    def available(self):
        return self.item is not None

    def update(self):
        """Prepare view related data."""
        self.context_state = queryMultiAdapter(
            (self.context, self.request),
            name='plone_context_state',
        )
        self.limit = self.config.get('limit_listings', 25)
        self._get_item()
        self._get_listings()

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(config.SETTINGS_DEVELOPMENT_COLLECTION, {})

    @property
    def batching(self):
        return ListingBatch(
            self.listings,
            self.limit,
            self.request.get('b_start', 0),
            orphan=1,
            batch_data=self._batching,
        )

    @property
    def listings(self):
        """Return listing results."""
        return self._listings

    def _get_item(self):
        cache = IAnnotations(self.request)
        self.item = cache.get('ps.plone.mls.development.traversed', None)

    def _get_listings(self):
        """Get the listings for the development.

        Optional filter by development phase or property group via GET
        params from the request.
        """
        item = self.item
        if item is None:
            return

        params = {
            'limit': self.limit,
            'offset': self.request.get('b_start', 0),
            'sort_on': 'last_activated_date',
            'reverse': '1',
        }

        phase_id = self.request.form.get('phase')
        group_id = self.request.form.get('group')

        if phase_id:
            try:
                item = api.DevelopmentPhase.get(self.item._api, phase_id)
            except exceptions.ResourceNotFound:
                item = None
        elif group_id:
            try:
                item = api.PropertyGroup.get(self.item._api, group_id)
            except exceptions.ResourceNotFound:
                item = None

        try:
            results, batching = item.listings(params=params)
        except exceptions.MLSError, e:
            logger.warn(e)
        else:
            self._listings = results
            self._batching = batching

    @memoize
    def view_url(self):
        """Generate view url."""
        try:
            item_id = self.item.id.value
        except Exception:
            item_id = ''

        return '/'.join([
            absoluteURL(self.context, self.request),
            item_id,
            '',
        ])
