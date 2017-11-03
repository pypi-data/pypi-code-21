# -*- coding: utf-8 -*-
"""Custom traversers for MLS Embedding items."""

# python imports
import copy

# zope imports
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.memoize.view import memoize
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import (
    IBrowserPublisher,
    IBrowserRequest,
)

# local imports
from ps.plone.mls import api
from ps.plone.mls.browser.developments.collection import (
    DevelopmentCollectionViewlet,
    EXCLUDED_SEARCH_FIELDS,
)
from ps.plone.mls.content import featured
from ps.plone.mls.interfaces import (
    IDevelopmentTraversable,
    IListingTraversable,
)


@implementer(IBrowserPublisher)
class MLSItemTraverser(DefaultPublishTraverse):
    """Custom Traverser for MLS Embedding items.

    The traverser looks for a MLS item id in the traversal stack and
    tries to call the corresponding details view. But before it does so, it
    tries to call all (currently) known traversers.

    It also does a check on the MLS item id. By default this one returns
    ``True``. But a subclass can override it to only return items
    that match a given condition.
    """

    detail_view_name = None
    item_id = 'item_id'

    def _lookup_add_on_traverser(self):
        """Call 3rd party traversers."""
        traverser_class = None
        try:
            from plone.app.imaging.traverse import ImageTraverser
        except ImportError:
            pass
        else:
            traverser_class = ImageTraverser

        try:
            from collective.contentleadimage.extender import LeadImageTraverse
        except ImportError:
            pass
        else:
            if not traverser_class:
                traverser_class = LeadImageTraverse

        return traverser_class

    def check_item(self, item_id):
        """Check if the MLS item with given ID is available."""
        return True

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        # Try to deliver the default content views.
        try:
            return super(MLSItemTraverser, self).publishTraverse(
                request, name,
            )
        except (NotFound, AttributeError):
            pass

        traverser_class = self._lookup_add_on_traverser()
        if traverser_class is not None:
            try:
                traverser = traverser_class(self.context, self.request)
                return traverser.publishTraverse(request, name)
            except (NotFound, AttributeError):
                pass
        name = self.pre_lookup(name)

        if not self.check_item(name):
            raise NotFound(self.context, name, request)

        self.post_lookup(name)

        if len(self.request.path) > 0:
            view_name = self.get_view_name_from_request()
        else:
            view_name = self.detail_view_name

        default_view = self.context.getDefaultLayout()

        # Let's call the detail view.
        view = queryMultiAdapter(
            (self.context, request), name=view_name,
        )
        if view is not None:
            return view

        # Deliver the default item view as fallback.
        view = queryMultiAdapter(
            (self.context, request), name=default_view,
        )
        if view is not None:
            return view

        raise NotFound(self.context, name, request)

    def pre_lookup(self, name):
        """Pre lookup hook."""
        return name.split('___')[0]

    def post_lookup(self, name):
        """Post lookup hook."""
        # We store the additional subpath for later reference.
        setattr(self.request, 'subpath', copy.copy(self.request.path))

        # We store the item_id parameter in the request.
        setattr(self.request, self.item_id, name)

    def get_view_name_from_request(self):
        view_name = None
        path = self.request.path
        if len(path) > 0:
            view_name = path.pop(-1)
            if view_name.startswith('@@'):
                view_name = view_name[2:]
        return view_name


@adapter(
    IDevelopmentTraversable,
    IBrowserRequest,
)
class DevelopmentTraverser(MLSItemTraverser):
    """Custom Traverser for Developments.

    See ``MLSItemTraverser`` for details.
    """

    __used_for__ = IDevelopmentTraversable
    detail_view_name = 'development-detail'
    item_id = 'development_id'
    has_development = False

    @memoize
    def check_item(self, item_id):
        """Check if the development ID is available."""
        dcv = DevelopmentCollectionViewlet(self.context, self.request, None)
        portal_state = queryMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state',
        )
        lang = portal_state.language()
        mlsapi = api.get_api(context=self.context, lang=lang)
        params = {'fields': u'id'}
        params.update(dcv.config)
        # params['limit'] = dcv.config.get('limit_developments', 5)
        params['limit'] = 1000
        params = api.prepare_search_params(
            params,
            context=self.context,
            omit=EXCLUDED_SEARCH_FIELDS,
        )
        try:
            result = api.Development.search(mlsapi, params=params)
        except Exception:
            return False

        available_ids = [item.id.value for item in result.get_items()]
        return item_id in available_ids

    def post_lookup(self, item_id):
        """Post lookup hook."""
        super(DevelopmentTraverser, self).post_lookup(item_id)
        portal_state = queryMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state',
        )
        lang = portal_state.language()
        item = api.get_development(
            item_id=item_id,
            context=self.context,
            request=self.request,
            lang=lang,
        )
        if item is not None:
            cache = IAnnotations(self.request)
            cache['ps.plone.mls.development.traversed'] = item
            self.has_development = True

    def get_view_name_from_request(self):
        view_name = None
        allowed_view_names = [
            'listings',
        ]
        path = self.request.path
        if len(path) < 1:
            return view_name

        view_name = path.pop(-1)
        if view_name.startswith('@@'):
            view_name = view_name[2:]

        if view_name in allowed_view_names:
            return view_name

        view_name = self.get_listing_view(view_name, additional=path)

        return view_name

    def get_listing_view(self, listing_id, additional=None):
        """"""
        allowed_view_names = [
            'print-listing',
        ]
        if not self.has_development:
            return

        # Check if the listing belongs to the development
        cache = IAnnotations(self.request)
        item = cache['ps.plone.mls.development.traversed']
        params = {
            'listing_ids': listing_id,
        }
        results, batch = item.listings(params=params)
        available_listings = [
            listing.get('id', {}).get('value', None) for listing in results
        ]
        if listing_id not in available_listings:
                raise NotFound(self.context, listing_id, self.request)

        setattr(self.request, 'listing_id', listing_id)

        while additional:
            name = additional.pop()
            if name in allowed_view_names:
                return name
            else:
                raise NotFound(self.context, name, self.request)
        return 'listing-detail'


@adapter(
    IListingTraversable,
    IBrowserRequest,
)
class ListingTraverser(MLSItemTraverser):
    """Custom Traverser for Listings.

    See ``MLSItemTraverser`` for details.
    """

    __used_for__ = IListingTraversable
    detail_view_name = 'listing-detail'
    item_id = 'listing_id'


@adapter(
    featured.IFeaturedListings,
    IBrowserRequest,
)
class FeaturedListingsTraverser(ListingTraverser):
    """Traverser for featured listings.

    It only allows listing ids which are defined in the context.
    """

    __used_for__ = featured.IFeaturedListings

    def check_item(self, item_id):
        """Check if the listing ID is available."""
        listing_ids = [lid.lower() for lid in self.context.listing_ids]
        return item_id.lower() in listing_ids
