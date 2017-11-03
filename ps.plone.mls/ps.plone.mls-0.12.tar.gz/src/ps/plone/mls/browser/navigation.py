# -*- coding: utf-8 -*-
"""Navigation Breadcrumb customizations."""

# zope imports
from Products.CMFPlone.browser.navigation import (
    PhysicalNavigationBreadcrumbs,
    get_view_url,
)
from zope.annotation.interfaces import IAnnotations

# local imports
from ps.plone.mls import _


TRAVERSE_TITLES = {
    'listings': _(u'Listings'),
}


class DevelopmentDetailsNavigationBreadcrumbs(PhysicalNavigationBreadcrumbs):
    """Custom breadcrumb navigation for development details."""

    def breadcrumbs(self):
        base = super(
            DevelopmentDetailsNavigationBreadcrumbs,
            self,
        ).breadcrumbs()

        name, item_url = get_view_url(self.context)

        development_id = getattr(self.request, 'development_id', None)
        last_item = self.request.steps[-2:-1]
        if development_id is None or self.context.id not in last_item:
            return base

        cache = IAnnotations(self.request)
        item = cache.get('ps.plone.mls.development.traversed', None)
        if item is None:
            return base

        try:
            title = item.title.value
        except Exception:
            return base

        url = '/'.join([item_url, development_id])

        base += ({
            'absolute_url': url,
            'Title': title,
        },)

        listing_id = getattr(self.request, 'listing_id', None)
        if listing_id is not None:
            base += ({
                'absolute_url': '/'.join([url, listing_id]),
                'Title': listing_id.upper(),
            },)

        subpath = getattr(self.request, 'subpath', [])
        if subpath and len(subpath) == 1:
            item = subpath[0]
            title = TRAVERSE_TITLES.get(item, None)
            if title is not None:
                base += ({
                    'absolute_url': '/'.join([url, item]),
                    'Title': title,
                },)

        return base


class ListingDetailsNavigationBreadcrumbs(PhysicalNavigationBreadcrumbs):
    """Custom breadcrumb navigation for listing details."""

    def breadcrumbs(self):
        base = super(ListingDetailsNavigationBreadcrumbs, self).breadcrumbs()

        name, item_url = get_view_url(self.context)

        item_id = getattr(self.request, 'listing_id', None)
        last_item = self.request.steps[-2:-1]
        if item_id is not None and self.context.id in last_item:
            base += ({
                'absolute_url': '/'.join([item_url, item_id]),
                'Title': item_id.upper(),
            },)

        return base
