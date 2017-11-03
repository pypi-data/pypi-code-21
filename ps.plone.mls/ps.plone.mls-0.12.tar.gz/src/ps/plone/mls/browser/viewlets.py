# -*- coding: utf-8 -*-
"""Customized plone viewlets."""

# zope imports
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.layout.viewlets import common
from plone.mls.listing.browser.interfaces import IListingDetails

# local imports
from ps.plone.mls.interfaces import (
    IDevelopmentDetails,
    IDevelopmentListings,
)
from ps.plone.mls import (
    _,
    utils,
)


class DublinCoreViewlet(common.DublinCoreViewlet):
    """Customized DublinCore descriptions for MLS embeddings."""

    def _get_dc_tags(self):
        """Generate the Dublin Core meta tags for an embedded item."""
        dc = {}

        if IListingDetails.providedBy(self.view):
            dc['DC.date.modified'] = self.view.data.get('modified')
            dc['DC.date.created'] = self.view.data.get('created')
            dc['DC.creator'] = self._get_mls_creator()
            dc['DC.type'] = u'MLS Listing'

        elif IDevelopmentDetails.providedBy(self.view):
            # Not yet implemented
            dc['DC.date.modified'] = None
            # Not yet implemented
            dc['DC.date.created'] = None
            dc['DC.creator'] = self._get_mls_creator()
            dc['DC.type'] = u'MLS Development'

        return dc

    def _get_mls_creator(self):
        """Get the creator/author from an embedded item."""
        if IListingDetails.providedBy(self.view):
            try:
                contact = self.view.contact
            except AttributeError:
                return
            else:
                return contact.get('agency', {}).get('name', {}).get('value')
        elif IDevelopmentDetails.providedBy(self.view):
            try:
                return self.view.item.agency().title.value
            except AttributeError:
                return

    def _get_mls_description(self):
        """Get the description from an embedded item."""
        description = None

        if IListingDetails.providedBy(self.view):
            try:
                description = self.view.description
            except AttributeError:
                return
        elif IDevelopmentDetails.providedBy(self.view):
            try:
                description = self.view.item.description.value
            except AttributeError:
                return

        description = utils.smart_truncate(description)
        return description

    @property
    def available(self):
        """Check if the preconditions are fullfilled."""
        is_development = IDevelopmentDetails.providedBy(self.view)
        is_listing = IListingDetails.providedBy(self.view)
        return is_development or is_listing

    def update(self):
        super(DublinCoreViewlet, self).update()

        if not self.available:
            return

        try:
            use_all = api.portal.get_registry_record(
                'plone.exposeDCMetaTags'
            )
        except InvalidParameterError:
            try:
                props = api.portal.get_tool(name='portal_properties')
                use_all = props.site_properties.exposeDCMetaTags
            except Exception:
                use_all = False

        meta_dict = dict(self.metatags)
        description = self._get_mls_description()

        if use_all:
            meta_dict['DC.description'] = description
            meta_dict.update(self._get_dc_tags())
        else:
            meta_dict['description'] = description

        self.metatags = meta_dict.items()


class TitleViewlet(common.TitleViewlet):
    """Customized title Viewlet for MLS embeddings."""

    def update(self):
        super(TitleViewlet, self).update()

        title = None
        if IDevelopmentDetails.providedBy(self.view):
            try:
                title = self.view.item.title.value
            except AttributeError:
                title = getattr(self.request, 'development_id', None)
        elif IListingDetails.providedBy(self.view):
            try:
                title = self.view.title
            except AttributeError:
                title = getattr(self.request, 'listing_id', None)
        elif IDevelopmentListings.providedBy(self.view):
            try:
                title = self.view.item.title.value
            except AttributeError:
                title = getattr(self.request, 'development_id', None)
            if title is not None:
                title = u'{0} &mdash; {1}'.format(
                    _(u'Listings'),
                    title,
                )

        if title is not None:
            self.site_title = u'{0} &mdash; {1}'.format(title, self.site_title)
