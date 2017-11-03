# -*- coding: utf-8 -*-
"""Featured Listings Viewlet."""

# zope imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.directives import form
from plone.memoize.view import memoize
from plone.mls.core.navigation import ListingBatch
from plone.mls.listing.api import prepare_search_params, search
from plone.mls.listing.browser.interfaces import IListingDetails
from plone.supermodel import model
from z3c.form import button
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
from zope.interface import Interface, alsoProvides, noLongerProvides
from zope.publisher.browser import BrowserView
from zope.traversing.browser.absoluteurl import absoluteURL

# local imports
from ps.plone.mls import (
    _,
    PLONE_4,
    PLONE_5,
)
from ps.plone.mls.interfaces import IListingTraversable


CONFIGURATION_KEY = 'ps.plone.mls.listing.featuredlistings'


class IPossibleFeaturedListings(Interface):
    """Marker interface for possible FeaturedListings viewlet."""


class IFeaturedListings(IListingTraversable):
    """Marker interface for FeaturedListings viewlet."""


class FeaturedListingsViewlet(ViewletBase):
    """Show featured MLS listings."""

    if PLONE_5:
        index = ViewPageTemplateFile('templates/listing_results_p5.pt')
    elif PLONE_4:
        index = ViewPageTemplateFile('templates/listing_results.pt')

    @property
    def available(self):
        return IFeaturedListings.providedBy(self.context) and \
            not IListingDetails.providedBy(self.view)

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(CONFIGURATION_KEY, {})

    def update(self):
        """Prepare view related data."""
        self._listings = None
        super(FeaturedListingsViewlet, self).update()
        self.context_state = queryMultiAdapter(
            (self.context, self.request), name='plone_context_state',
        )
        self.limit = self.config.get('limit', 25)
        self._get_listings()

    def _get_listings(self):
        """Query the recent listings from the MLS."""
        listing_ids = self.config.get('listing_ids', [])
        if len(listing_ids) == 0:
            return
        listing_ids = [lid.lower() for lid in listing_ids]
        params = {
            'limit': 0,
            'offset': 0,
            'lang': self.portal_state.language(),
        }
        params.update(self.config)
        params['listing_ids'] = listing_ids
        params = prepare_search_params(params)
        results = search(params, batching=False, context=self.context)
        if results is None or len(results) == 0:
            return

        # sort the results based on the listing_ids
        results = [(item['id']['value'], item) for item in results]
        results = dict(results)
        self._listings = [
            results.get(id) for id in listing_ids if id in results
        ]

    @property
    @memoize
    def listings(self):
        """Return listing results."""
        return self._listings

    @memoize
    def view_url(self):
        """Generate view url."""
        if not self.context_state.is_view_template():
            return self.context_state.current_base_url()
        else:
            return absoluteURL(self.context, self.request) + '/'

    @property
    def batching(self):
        return ListingBatch(
            self.listings, self.limit, self.request.get('b_start', 0),
            orphan=1,
            batch_data=None,
        )


class IFeaturedListingsConfiguration(model.Schema):
    """Featured Listings Configuration Form Schema."""

    listing_ids = schema.List(
        description=_(
            u'Add one Listing ID per line for each entry to show up.'
        ),
        title=_(u'MLS Listing IDs'),
        unique=True,
        value_type=schema.TextLine(
            title=_(u'ID'),
        ),
    )


class FeaturedListingsConfiguration(form.SchemaForm):
    """Featured Listings Configuration Form."""

    schema = IFeaturedListingsConfiguration

    label = _(u'\'Featured Listings\' Configuration')
    description = _(
        u'Adjust the behaviour for this \'Featured Listings\' viewlet.'
    )

    def getContent(self):
        annotations = IAnnotations(self.context)
        return annotations.get(
            CONFIGURATION_KEY, annotations.setdefault(CONFIGURATION_KEY, {}),
        )

    @button.buttonAndHandler(_(u'Save'))
    def handle_save(self, action):
        data, errors = self.extractData()
        if not errors:
            annotations = IAnnotations(self.context)
            annotations[CONFIGURATION_KEY] = data
            self.request.response.redirect(
                absoluteURL(self.context, self.request),
            )

    @button.buttonAndHandler(_(u'Cancel'))
    def handle_cancel(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request))


class FeaturedListingsStatus(object):
    """Return activation/deactivation status of FeaturedListings viewlet."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        return IPossibleFeaturedListings.providedBy(self.context) and \
            not IFeaturedListings.providedBy(self.context)

    @property
    def active(self):
        return IFeaturedListings.providedBy(self.context)


class FeaturedListingsToggle(object):
    """Toggle FeaturedListings viewlet for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        msg_type = 'info'

        if IFeaturedListings.providedBy(self.context):
            # Deactivate FeaturedListings viewlet.
            noLongerProvides(self.context, IFeaturedListings)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'\'Featured Listings\' viewlet deactivated.')
        elif IPossibleFeaturedListings.providedBy(self.context):
            alsoProvides(self.context, IFeaturedListings)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'\'Featured Listings\' viewlet activated.')
        else:
            msg = _(
                u'The \'Featured Listings\' viewlet does\'t work with this '
                u'content type. Add \'IPossibleFeaturedListings\' to the '
                u'provided interfaces to enable this feature.'
            )
            msg_type = 'error'

        api.portal.show_message(
            message=msg, request=self.request, type=msg_type,
        )
        self.request.response.redirect(self.context.absolute_url())


class FeaturedListings(BrowserView):
    """Featured Listings view"""

    limit = 25

    def __init__(self, context, request):
        super(FeaturedListings, self).__init__(context, request)
        self.portal_state = queryMultiAdapter(
            (self.context, self.request), name='plone_portal_state',
        )

    def _get_listings(self):
        """Query the recent listings from the MLS."""
        listing_ids = self.context.listing_ids
        if len(listing_ids) == 0:
            return
        listing_ids = [lid.lower() for lid in listing_ids]
        params = {
            'limit': 0,
            'offset': 0,
            'lang': self.portal_state.language(),
        }
        params.update({
            'listing_ids': listing_ids,
        })
        params = prepare_search_params(params)
        results = search(params, batching=False, context=self.context)
        if results is None or len(results) == 0:
            return

        # sort the results based on the listing_ids
        results = [(item['id']['value'], item) for item in results]
        results = dict(results)
        return [results.get(id) for id in listing_ids if id in results]

    @property
    @memoize
    def listings(self):
        """Return listing results."""
        return self._get_listings()

    @property
    def batching(self):
        return ListingBatch(
            self.listings,
            self.limit,
            self.request.get('b_start', 0),
            orphan=1,
            batch_data=None,
        )
